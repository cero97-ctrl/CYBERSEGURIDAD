# modulos .py
import socket
import whois
import dns . resolver
from concurrent . futures import ThreadPoolExecutor

#==============================================================================
# MODULO 1: RECONOCIMIENTO DNS Y WHOIS ( BASE )
#==============================================================================

def get_dns_info ( domain ) :
    """
    Realiza consultas WHOIS y DNS para un dominio dado y muestra la
    informacion .
    """
    print ( f"\n[+] Obteniendo informacion WHOIS para : { domain }")
    try:
        w = whois . whois ( domain )
        print (" [ -] Registrante :", w . registrar )
        print (" [ -] Servidores de Nombres :", w . name_servers )
    except Exception as e :
        print ( f" [!] No se pudo obtener informacion WHOIS : {e}")

        print ( f"\n[+] Realizando consultas DNS para : { domain }")

    record_types = [ 'A', 'AAAA ', 'MX ', 'NS ', 'TXT ', 'SOA ']
    for record_type in record_types :
        try:
            answers = dns . resolver . resolve ( domain , record_type )
            print ( f" [ -] Registros { record_type }:")
            for rdata in answers :
                    print ( f" { rdata . to_text ()}")
        except ( dns . resolver . NoAnswer , dns . resolver . NXDOMAIN ) :
            print ( f" [!] No se encontraron registros { record_type }.")
        except Exception as e :
            print ( f" [!] Error consultando registros { record_type }: {e}")
#==============================================================================
# Tarea: Crear un script para obtener los registros TXT (informacion descriptiva,
#como SPF) y SOA (inicio de autoridad) de un dominio.
#==============================================================================
def get_txt_soa_records(domain): 
    """
    Realiza consultas  DNS para un dominio dado y muestra la
    informacion TXT y SOA.
    """
    
    record_types = [ 'TXT ', 'SOA ']
    for record_type in record_types :
        try:
            answers = dns . resolver . resolve ( domain , record_type )
            print ( f" [ -] Registros { record_type }:")
            for rdata in answers :
                    print ( f" { rdata . to_text ()}")
        except ( dns . resolver . NoAnswer , dns . resolver . NXDOMAIN ) :
            print ( f" [!] No se encontraron registros { record_type }.")
        except Exception as e :
            print ( f" [!] Error consultando registros { record_type }: {e}")

#==============================================================================
# MODULO 2: ESCANER DE PUERTOS ( BASE )
# ( Este modulo se usara en tareas futuras )
#==============================================================================

def scan_ports ( target , port_spec ) :
    """
    Escanea los puertos especificados en el host objetivo .
    ( Implementacion pendiente para futuras tareas )
    """
    print ( f"[!] El modulo de escaneo de puertos para ’{ port_spec } ’ aunesta implementado .")
    return []
