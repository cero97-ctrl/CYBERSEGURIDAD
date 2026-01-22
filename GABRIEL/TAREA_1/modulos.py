import dns.resolver

# ==================================
# MODULO 1: RECONOCIMIENTO DNS
# ==================================

def get_dns_info(domain):
    """
    Realiza consultas DNS (A y AAAA) y muestra la informacion.
    """
    print(f"\n[+] Realizando consultas DNS para: {domain}")

    record_types = ['A', 'AAAA']

    for record_type in record_types:
        try:
            # Se obtienen todos los registros
            answers = dns.resolver.resolve(domain, record_type)

            print(f"  [-] Registros {record_type}:")

            # Se imprimen cada uno de los registros solicitados
            for rdata in answers:
                print(f"    {rdata.to_text()}")

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            print(f"  [!] No se encontraron registros {record_type}.")
        except Exception as e:
            print(f"  [!] Error consultando registros {record_type}: {e}")
