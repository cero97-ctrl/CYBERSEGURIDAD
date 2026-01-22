# auditoria.py
import argparse
import modulos  # Importamos nuestro archivo de modulos

def main():
    # --- Configuracion de Argumentos ---
    parser = argparse.ArgumentParser(
        description="Herramienta de Auditoria de Seguridad Informatica.",
        epilog="Ejemplo de uso: python auditoria.py example.com --dns --scan '1-1024'")
    parser.add_argument("target", help="El objetivo (dominio o IP) a auditar.")

    # Argumentos para seleccionar los modulos a ejecutar
    parser.add_argument("--dns",
                       action="store_true",
                       help="Ejecuta el modulo de reconocimiento DNS y WHOIS.")
    parser.add_argument("--scan",
                       metavar="PUERTOS",
                       help="Ejecuta el escaner de puertos. E.g., '21,22,80' o '1-1024'.")
    parser.add_argument("--dns-txtsoa",
                       action="store_true",
                       help="Ejecuta el modulo de reconocimiento DNS Para TXT y SOA.")
    args = parser.parse_args()
    
    target = args.target
    print(f"[*] Iniciando auditoria para el objetivo: {target}\n")
    
    # --- Logica para llamar a los modulos ---
    if args.dns:
        print("\n" + "="*20 + " MODULO: RECONOCIMIENTO DNS Y WHOIS " + "="*20)
        modulos.get_dns_info(target)
        print("=" * 65)
    
    if args.dns_txtsoa:
        print("\n" + "="*20 + " MODULO: RECONOCIMIENTO DNS TXT SOA" + "="*20)
        modulos.get_txt_soa_records(target)
        print("=" * 65)
   
    if args.scan:
        print("\n" + "="*20 + " MODULO: ESCANER DE PUERTOS " + "="*25)
        open_ports = modulos.scan_ports(target, args.scan)
        print(f"\n[+] Escaneo de puertos finalizado. Se encontraron {len(open_ports)} puertos abiertos.")
        print("=" * 65)

    print("\n[*] Auditoria finalizada.")

if __name__ == "__main__":
    main()