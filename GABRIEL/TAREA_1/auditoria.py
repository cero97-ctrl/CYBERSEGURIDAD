import argparse
import modulos  # Importar modulos


def main():
    # --- Configuracion de Argumentos ---
    parser = argparse.ArgumentParser(
        description="Herramienta de Auditoria de Seguridad Informatica.",
        epilog="Ejemplo de uso: python auditoria.py example.com --dns"
    )

    parser.add_argument("target", help="El objetivo (dominio o IP) a auditar.")

    # Argumentos para seleccionar los modulos a ejecutar
    parser.add_argument(
        "--dns",
        action="store_true",
        help="Ejecuta el modulo de reconocimiento DNS (solo A y AAAA)."
    )


    args = parser.parse_args()
    target = args.target

    print(f"[*] Iniciando auditoria para el objetivo: {target}\n")

    # --- Logica para llamar a los modulos ---
    if args.dns:
        print("\n" + "=" * 20 + " MODULO: DNS (A/AAAA) " + "=" * 20)
        modulos.get_dns_info(target)
        print("=" * 67)


    print("\n[*] Auditoria finalizada.")


if __name__ == "__main__":
    main()