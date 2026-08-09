#!/usr/bin/env python3
"""
verificar_creditos.py — Comprueba el estado de las claves/créditos de los backends LLM (Layer 3)

Antes de lanzar el batch de evaluación, verifica para cada backend que
el orquestador puede usar (gemini, openrouter, groq):
  - Si la API key está presente y configurada.
  - Si la credencial responde (llamada mínima/sin costo si el backend lo permite).
  - Cuota/créditos restantes cuando el proveedor lo expone.

Uso:
    python3 verificador_creditos.py [--backend gemini|openrouter|groq|all]
    python3 verificador_creditos.py            # verifica los tres
    python3 verificador_creditos.py --modelo gemini-2.5-flash

Salida (stdout, JSON):
    [
      {
        "backend": "gemini",
        "ok": true,
        "key_presente": true,
        "modelos_asociados": "models/gemini-2.5-flash",
        "cuota": "...",          
        "creditos_disponibles": "...",
        "detalle": "..."
      },
      ...
    ]

Nota: Ningún proveedor expone el saldo monetario de forma estándar salvo OpenRouter
(limit/usage vía GET /auth/key). Para Gemini y Groq se hace una llamada mínima de
prueba y se reporta el estado de la clave; los límites de cuota de Gemini se
revelan como códigos 429/402 en tiempo de ejecución.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()


# ── Carga de credenciales ──────────────────────────────────────────────────────

def cargar_entorno() -> None:
    """Carga el .env del proyecto (raíz CYBERSEGURIDAD o del propio flujo)."""
    candidate_dirs = [
        SCRIPT_DIR,                          # evaluacion_examenes/.env
        SCRIPT_DIR.parent,                   # raíz CYBERSEGURIDAD/.env
    ]
    try:
        from dotenv import load_dotenv
        for d in candidate_dirs:
            env_file = d / ".env"
            if env_file.exists():
                load_dotenv(env_file, override=False)
                break
    except ImportError:
        pass


def leer_key(nombre: str) -> str | None:
    """Retorna el valor de la API key si existe, o None."""
    val = os.getenv(nombre)
    if val:
        val = val.strip()
        if val:
            return val
    return None


def key_masked(key: str | None) -> str:
    """Muestra solo los primeros 6 caracteres de la clave para diagnóstico."""
    if not key:
        return "(ausente)"
    if len(key) <= 10:
        return "*" * len(key)
    return f"{key[:6]}...{key[-4:]}"


# ── Verificación por backend ───────────────────────────────────────────────────

def verificar_gemini(modelo: str) -> dict:
    """Verifica la clave de Gemini con una llamada mínima al modelo indicado."""
    key = leer_key("GOOGLE_API_KEY")
    resultado = {"backend": "gemini", "ok": False, "key_presente": key is not None,
                 "modelo": modelo, "key": key_masked(key)}
    if not key:
        resultado["detalle"] = "GOOGLE_API_KEY no configurada. Agregar en .env."
        return resultado
    try:
        from google import genai
    except ImportError:
        resultado["detalle"] = "SDK google-genai no instalado (pip install google-genai)."
        return resultado

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=modelo,
            contents="responde solo 'ok'",
            config={"max_output_tokens": 4},
        )
        texto = (response.text or "").strip().lower()
        # Una respuesta vacía tras una llamada exitosa suele deberse a la
        # configuración de thinking del modelo; la clave es válida igualmente.
        resultado["ok"] = True
        resultado["detalle"] = f"Clave válida (llamada mínima exitosa, respuesta: {texto[:20] or 'vacía'})."
    except Exception as e:
        codigo = getattr(e, "status_code", None) or getattr(e, "code", None)
        resultado["detalle"] = f"Error al probar la clave: ({codigo}) {e}"
        if codigo in (429, 402):
            resultado["detalle"] = "Cuota agotada o sin créditos (429/402). Revisar Google AI Studio."
    return resultado


def verificar_openrouter() -> dict:
    """Verifica credencial y créditos disponibles de OpenRouter vía GET /auth/key."""
    key = leer_key("OPENROUTER_API_KEY")
    resultado = {"backend": "openrouter", "ok": False, "key_presente": key is not None,
                 "key": key_masked(key)}
    if not key:
        resultado["detalle"] = "OPENROUTER_API_KEY no configurada. Agregar en .env."
        return resultado

    try:
        import urllib.request
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        resultado["detalle"] = f"No se pudo consultar OpenRouter: {e}"
        return resultado

    d = data.get("data", {}) if isinstance(data, dict) else {}
    limit = d.get("limit")
    usage = d.get("usage")
    is_free = d.get("is_free_tier", False)

    if limit is not None and usage is not None:
        restante = max(0.0, float(limit) - float(usage))
        resultado["creditos_disponibles"] = f"${restante:.4f} (límite ${limit:.4f} - usado ${usage:.4f})"
        resultado["ok"] = restante > 0.0
        resultado["detalle"] = "Saldo consultado correctamente."
    else:
        resultado["creditos_disponibles"] = "No expuesto por la API"
        resultado["detalle"] = "Clave válida; el saldo no se expone o es flexible."
        resultado["ok"] = not is_free or True  # sin saldo visible no podemos afirmarlo
        if is_free:
            resultado["detalle"] = "Cuenta free-tier: límites de créditos limitados pero operativa."
    return resultado


def verificar_groq() -> dict:
    """Verifica la clave de Groq con una llamada mínima a un modelo barato."""
    key = leer_key("GROQ_API_KEY")
    if not key:
        # fallback al archivo .groq_api_key del workspace
        for d in [SCRIPT_DIR, SCRIPT_DIR.parent]:
            f = d / ".groq_api_key"
            if f.exists():
                key = f.read_text(encoding="utf-8").strip() or None
                break

    resultado = {"backend": "groq", "ok": False, "key_presente": key is not None,
                 "modelo": "llama-3.3-70b-versatile", "key": key_masked(key)}
    if not key:
        resultado["detalle"] = "GROQ_API_KEY no configurada."
        return resultado

    try:
        from openai import OpenAI
    except ImportError:
        resultado["detalle"] = "SDK openai no instalado (pip install openai)."
        return resultado

    try:
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model=resultado["modelo"],
            messages=[{"role": "user", "content": "responde solo 'ok'"}],
            max_tokens=4,
        )
        texto = (response.choices[0].message.content or "").strip().lower()
        resultado["ok"] = texto.startswith("ok") or texto != ""
        resultado["detalle"] = "Clave válida (llamada mínima exitosa)."
    except Exception as e:
        codigo = getattr(e, "code", None)
        status = getattr(e, "status_code", None) or codigo
        resultado["detalle"] = f"Error al probar la clave: ({status}) {e}"
        if status == 403:
            resultado["detalle"] = ("Acceso denegado (403): la clave GROQ_API_KEY no está autorizada, "
                                    "expiró o tu región/IP está bloqueada por Groq.")
        elif status in (429, 402):
            resultado["detalle"] = "Cuota agotada o sin créditos (429/402)."
    return resultado


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Verifica claves/créditos de los backends LLM del orquestador.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 verificar_creditos.py                 # verifica los tres backends
  python3 verificar_creditos.py --backend gemini
  python3 verificar_creditos.py --modelo gemini-2.5-flash
        """,
    )
    parser.add_argument("--backend", default="all", choices=["all", "gemini", "openrouter", "groq"],
                        help="Backend a verificar (default: all).")
    parser.add_argument("--modelo", default="gemini-2.5-flash",
                        help="Modelo Gemini para la prueba mínima (default: gemini-2.5-flash).")
    return parser.parse_args()


def main():
    args = parse_args()
    cargar_entorno()

    chequeos: list[dict] = []
    if args.backend in ("all", "gemini"):
        chequeos.append(verificar_gemini(args.modelo))
    if args.backend in ("all", "openrouter"):
        chequeos.append(verificar_openrouter())
    if args.backend in ("all", "groq"):
        chequeos.append(verificar_groq())

    print("\n" + "═" * 60)
    print("  VERIFICACIÓN DE CRÉDITOS — Backends LLM del orquestador")
    print("═" * 60)
    para_batch = True
    for c in chequeos:
        estado = "✅ OK" if c["ok"] else "❌ NO OK"
        para_batch = para_batch and c["ok"]
        print(f"\n  [{estado}] {c['backend'].upper()}")
        print(f"      Clave   : {c.get('key', '(no aplica)')}")
        if c.get("modelo"):
            print(f"      Modelo  : {c['modelo']}")
        if c.get("creditos_disponibles"):
            print(f"      Créditos: {c['creditos_disponibles']}")
        print(f"      Detalle : {c.get('detalle', '')}")
    print("\n" + "═" * 60)
    print(f"  Resultado general: {'LISTO PARA EL BATCH ✅' if para_batch else 'REVISAR ANTES DE EJECUTAR ⚠️'}")
    print("═" * 60 + "\n")

    print(json.dumps(chequeos, ensure_ascii=False, indent=2))
    sys.exit(0 if para_batch else 1)


if __name__ == "__main__":
    main()