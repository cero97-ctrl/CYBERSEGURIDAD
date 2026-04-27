# auditoria.py
import argparse
import sys
import json
import os

try:
    from jsonschema import validate
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Validación pre-importación de los archivos de módulos
modulos_esperados = ["dns_recon.py", "osint.py", "discovery.py", "scanning.py"]
directorio_modulos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulos")

for modulo in modulos_esperados:
    if not os.path.isfile(os.path.join(directorio_modulos, modulo)):
        print(f"\n[!] ERROR CRÍTICO: Falta el archivo '{modulo}' en la carpeta 'modulos/'.")
        print("    Recuerda la 'Regla de Oro': Los scripts de los grupos deben mantener sus")
        print("    nombres originales (dns_recon.py, osint.py, discovery.py, scanning.py).")
        print("    Por favor, verifica que no haya sido renombrado o eliminado.\n")
        sys.exit(1)

from modulos import dns_recon   # Grupo 1
from modulos import osint       # Grupo 2
from modulos import discovery   # Grupo 3
from modulos import scanning    # Grupo 4

def validar_resultado(resultado):
    """
    Verifica si el diccionario retornado por un modulo cumple con el esquema oficial.
    """
    if resultado is None:
        return

    if not HAS_JSONSCHEMA:
        print("  [!] Aviso: Libreria 'jsonschema' no encontrada. Omitiendo validacion estricta.")
        print("      Instale con: pip install jsonschema")
        return

    schema_path = os.path.join(os.path.dirname(__file__), "docs/schema_resultados.json")
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        validate(instance=resultado, schema=schema)
        print(f"  [OK] Validacion de esquema exitosa para: {resultado.get('modulo')} (Estudiante: {resultado.get('estudiante')})")
    except Exception as e:
        print(f"  [X] ERROR DE CONTRATO en modulo '{resultado.get('modulo', 'Desconocido')}':")
        print(f"      Detalle: {str(e)}")

def ejecutar_modulo(func, *args, **kwargs):
    """
    Ejecuta una funcion de modulo de forma segura y valida su resultado.
    """
    try:
        resultado = func(*args, **kwargs)
        if resultado:
            validar_resultado(resultado)
            return resultado
    except NotImplementedError as e:
        print(f"\n[!] Característica en desarrollo: {e}")
    except Exception as e:
        print(f"\n[!] Error inesperado en {func.__name__}: {e}")
    return None

def guardar_historial(resultados):
    """
    Guarda la lista de resultados en un archivo JSON para mantener un historial.
    """
    if not resultados:
        return

    archivo_historial = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historial_auditoria.json")
    historial = []

    if os.path.isfile(archivo_historial):
        try:
            with open(archivo_historial, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except json.JSONDecodeError:
            pass # Si el archivo está corrupto o vacío, iniciamos de cero

    historial.extend(resultados)

    with open(archivo_historial, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)
    print(f"\n[*] Historial guardado exitosamente. Se agregaron {len(resultados)} registro(s) a 'historial_auditoria.json'.")

def main():
    parser = argparse.ArgumentParser(
        description="Suite de Auditoria de Seguridad Informatica - Python",
        epilog="Uso: python auditoria.py target.com --dns-all"
    )
    
    parser.add_argument("target", help="Dominio o IP objetivo")

    # Grupo para Recopilacion de Informacion
    recon_group = parser.add_argument_group('Recopilacion de Informacion')
    recon_group.add_argument("--dns-all", action="store_true", help="Ejecuta todos los checks DNS/WHOIS")
    recon_group.add_argument("--dns-a", action="store_true", help="Registros A/AAAA (G1-E1)")
    recon_group.add_argument("--dns-mxns", action="store_true", help="Registros MX/NS (G1-E2)")
    recon_group.add_argument("--dns-txtsoa", action="store_true", help="Registros TXT/SOA (G1-E3)")
    
    # Grupo OSINT (Grupo 2)
    osint_group = parser.add_argument_group('OSINT y Huella Digital')
    osint_group.add_argument("--whois", action="store_true", help="Consulta WHOIS (G2-E1)")
    osint_group.add_argument("--dorks", action="store_true", help="Búsqueda de subdominios/dorks (G2-E2/E3)")

    # Grupo para Escaneo
    scan_group = parser.add_argument_group('Escaneo de Puertos')
    scan_group.add_argument("--scan", metavar="PUERTOS", help="Escaneo TCP/UDP (Grupo 4)")
    scan_group.add_argument("--ping-sweep", action="store_true", help="Descubrimiento de hosts (Grupo 3)")

    args = parser.parse_args()

    print(f"[*] Iniciando auditoria para: {args.target}")

    resultados_totales = []

    # Ejecución modular con manejo de errores individual
    try:
        if args.dns_all or args.dns_a:
            res = ejecutar_modulo(dns_recon.get_a_records, args.target)
            if res: resultados_totales.append(res)
        
        if args.dns_all or args.dns_mxns:
            res = ejecutar_modulo(dns_recon.get_mx_ns_records, args.target)
            if res: resultados_totales.append(res)
            
        if args.dns_all or args.dns_txtsoa:
            res = ejecutar_modulo(dns_recon.get_txt_soa_records, args.target)
            if res: resultados_totales.append(res)

        if args.whois:
            res = ejecutar_modulo(osint.get_whois_data, args.target)
            if res: resultados_totales.append(res)

        if args.dorks:
            # Ejecuta la función del Estudiante 2 (Subdominios)
            res_dorks = ejecutar_modulo(osint.get_subdomains_via_dorks, args.target)
            if res_dorks: resultados_totales.append(res_dorks)
            # Ejecuta la función del Estudiante 3 (Archivos expuestos)
            res_archivos = ejecutar_modulo(osint.check_archivos_expuestos, args.target)
            if res_archivos: resultados_totales.append(res_archivos)

        if args.ping_sweep:
            res = ejecutar_modulo(discovery.ping_sweep, args.target)
            if res: resultados_totales.append(res)

        if args.scan:
            res = ejecutar_modulo(scanning.scan_ports_dispatcher, args.target, args.scan)
            if res: resultados_totales.append(res)

        guardar_historial(resultados_totales)
    except AttributeError as e:
        print(f"\n[!] Error en la estructura de los módulos: {e}")

    except KeyboardInterrupt:
        print("\n[!] Auditoria interrumpida por el usuario.")
        sys.exit(1)

if __name__ == "__main__":
    main()