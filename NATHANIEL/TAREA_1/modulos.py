import whois
import dns.resolver

# --- MÓDULO 1: RECONOCIMIENTO DNS ---

def get_mx_ns_records(domain):
    print(f"\n[+] Realizando consultas DNS para: {domain}")
    record_types = [ 'MX', 'NS', ]

    for record_type in record_types:
        try:

            answers = dns.resolver.resolve(domain, record_type)
            print(f" [-] Registros {record_type}:")
            for rdata in answers:
                print(f"    {rdata.to_text()}")

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            print(f" [!] No se encontraron registros {record_type}.")
        except Exception as e:
            print(f" [!] Error consultando registros {record_type}: {e}")

    return []