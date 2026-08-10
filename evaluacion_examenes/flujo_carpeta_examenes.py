#!/usr/bin/env python3
"""
flujo_carpeta_examenes.py — BATCH: evalúa todos los exámenes de una carpeta (Layer 2)

Recorre todos los PDFs de <carpeta_examenes> y ejecuta flujo_evaluar_examen.py por cada uno.
Los informes .tex/.pdf se guardan en <carpeta_padre>/informe_examen/. Al final escribe
un resumen JSON (.tmp/resumen_lote.json) y muestra una tabla con los puntajes.

Uso:
    python3 flujo_carpeta_examenes.py --carpeta examenes-teoricos/03/examen_estudiante
    python3 flujo_carpeta_examenes.py --carpeta <ruta> [--modelo gemini-2.5-flash] [--dpi 250]
    python3 flujo_carpeta_examenes.py --carpeta <ruta> [--solo <glob_pdf>] [--api-backend gemini]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PYTHON     = sys.executable
FLUJO      = SCRIPT_DIR / "flujo_evaluar_examen.py"
TMP_DIR    = SCRIPT_DIR / ".tmp"
RESUMEN    = TMP_DIR / "resumen_lote.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(
        description="Evalúa en lote todos los exámenes de una carpeta.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 flujo_carpeta_examenes.py --carpeta examenes-teoricos/03/examen_estudiante
  python3 flujo_carpeta_examenes.py --carpeta <ruta> --dpi 300
  python3 flujo_carpeta_examenes.py --carpeta <ruta> --solo Cesar_Leon.pdf
        """,
    )
    parser.add_argument("--carpeta", required=True,
                        help="Carpeta con los PDFs de exámenes de estudiantes.")
    parser.add_argument("--modelo", default="gemini-2.5-flash",
                        help="Modelo a usar (default: gemini-2.5-flash).")
    parser.add_argument("--api-backend", default="gemini",
                        choices=["gemini", "openrouter", "groq", "huggingface"],
                        help="Backend de API (default: gemini).")
    parser.add_argument("--dpi", type=int, default=250,
                        help="DPI de renderizado (default: 250).")
    parser.add_argument("--rubrica", default=None,
                        help="(Opcional) Rúbrica YAML común a todos los exámenes.")
    parser.add_argument("--solo", default=None,
                        help="(Opcional) Procesar solo un PDF concreto (nombre de archivo).")
    args = parser.parse_args()

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"  ❌  Carpeta no encontrada: {args.carpeta}", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(carpeta.glob("*.pdf"))
    if args.solo:
        pdf = Path(args.solo) if Path(args.solo).is_absolute() else carpeta / args.solo
        pdfs = [pdf]
    pdfs = [p for p in pdfs if p.exists()]

    if not pdfs:
        print("  ❌  No se encontraron PDFs en la carpeta.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'═'*56}")
    print(f"  SEGURIDAD INFORMÁTICA — Evaluación en Lote de Exámenes")
    print(f"{'═'*56}")
    print(f"  Carpeta : {carpeta}")
    print(f"  PDFs    : {len(pdfs)}")
    print(f"  Modelo  : {args.modelo}")
    print(f"  Backend : {args.api_backend}  |  DPI: {args.dpi}")
    print(f"{'═'*56}\n")

    TMP_DIR.mkdir(exist_ok=True)
    resultados = []

    for i, pdf in enumerate(pdfs, start=1):
        print(f"\n{'─'*56}")
        print(f"  [{i}/{len(pdfs)}] Evaluando: {pdf.name}")
        print(f"{'─'*56}")

        cmd = [PYTHON, str(FLUJO), "--pdf", str(pdf),
               "--modelo", args.modelo, "--api-backend", args.api_backend,
               "--dpi", str(args.dpi)]
        if args.rubrica:
            cmd += ["--rubrica", args.rubrica]

        proc = subprocess.run(cmd, text=True, encoding="utf-8")

        resultados.append({
            "pdf": pdf.name,
            "estado": "ok" if proc.returncode == 0 else "error",
            "exit_code": proc.returncode,
        })

    # ── Ordenar resumen y escribir JSON ─────────────────────────────────────────
    resultados.sort(key=lambda r: r["pdf"])
    for r in resultados:
        r["updated_at"] = now_iso()
    total_ok = sum(1 for r in resultados if r["estado"] == "ok")

    resultado_batch = {
        "carpeta": str(carpeta.resolve()),
        "total_pdfs": len(resultados),
        "total_ok": total_ok,
        "total_error": len(resultados) - total_ok,
        "estudiantes": resultados,
        "finished_at": now_iso(),
    }
    RESUMEN.write_text(json.dumps(resultado_batch, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'═'*56}")
    print(f"  BATCH COMPLETADO — {len(resultados)} exámenes procesados")
    print(f"{'═'*56}")
    for r in resultados:
        estado = "✅ ok" if r["estado"] == "ok" else f"❌ error ({r.get('exit_code', '?')})"
        print(f"  {r['pdf']:40s} {estado}")
    print(f"{'═'*56}")
    print(f"  Resumen JSON: {RESUMEN}")
    print(f"{'═'*56}\n")

    sys.exit(0 if total_ok == len(resultados) else 1)


if __name__ == "__main__":
    main()