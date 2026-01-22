import argparse
import modulos
# Importamos nuestro archivo de modulos.

def main():
    """
   # Funcion principal para parsear argumentos y llamar a los modulos
   # correspondientes.
    """
    parser = argparse.ArgumentParser(
        description="Herramienta de Auditoria de Red y DNS.",
        epilog="Ejemplo de uso: python auditoria.py google.com --dns-mxns"
    )

    # Argumento posicional obligatorio
    parser.add_argument("domain", help="El dominio objetivo para la auditoria.")

    # Grupo de argumentos mutuamente excluyentes (solo se puede elegir uno)
    # Hacemos que al menos una accion sea requerida.
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--dns-all",
        action="store_true",
        help="Realiza auditoria DNS completa (WHOIS, A, AAAA, MX, NS, TXT, SOA)."
    )

    # Tarea 3: Añadir el nuevo argumento --dns-mxns
    group.add_argument(
        "--dns-mxns",
        action="store_true",
        help="Obtiene unicamente los registros MX y NS del dominio."
    )

    group.add_argument(
        "--scan-ports",
        metavar="PUERTOS",
       help="Escanea puertos especificos (ej: '80,443' o '1-1024')."
    )


    args = parser.parse_args()
    domain = args.domain
    
   # Lógica para llamar a la funcion correcta segun el argumento
    if args.dns_all:
        modulos.get_dns_info(domain)

    elif args.dns_mxns:
        # Tarea 3: Llamada a la nueva funcion
        modulos.get_mx_ns_records(domain)

    elif args.scan_ports:
        modulos.scan_ports(domain, args.scan_ports)

if __name__ == "__main__":
    main()