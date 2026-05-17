# Grupo 1: Reconocimiento DNS (3 estudiantes)
import dns.resolver
from typing import Dict, Any
from datetime import datetime

def get_a_records(domain: str) -> Dict[str, Any]:
    """
    Consulta los registros DNS de tipo A (IPv4) y AAAA (IPv6) para un dominio.

    Args:
        domain (str): El nombre de dominio a investigar (ej. 'google.com').

    Returns:
        Dict[str, Any]: Diccionario con los resultados de la auditoria, 
        siguiendo el formato definido en schema_resultados.json.
    """
    print(f"  [G1-E1] Consultando registros A/AAAA para: {domain}")
    
    #Estructura del resultado
    resultado = {
        "modulo": "DNS",
        "grupo": 1,
        "estudiante": "Jeanpiere Mendoza",
        "target": domain,
        "timestamp": datetime.utcnow().isoformat(),
        "querytype": "A_AAAA",
        "data": {
            "A": [],
            "AAAA": []
        },
        "status": "success",
        "error": None
    }

    #Consulta DNS tipo A
    try:
        respuestas_a = dns.resolver.resolve(domain, 'A')
        for rdata in respuestas_a:
            resultado["data"]["A"].append(str(rdata.address))

    except dns.resolver.NoAnswer:
        print("No hay registros A")
        pass

    except dns.resolver.NXDOMAIN:
        resultado["status"] = "error"
        resultado["error"] = f"El dominio '{domain}' no existe (NXDOMAIN)."
        return resultado
    
    except dns.resolver.NoNameservers:
        resultado["status"] = "error"
        resultado["error"] = f"No se pudo contactar con los servidores DNS para '{domain}'."
        return resultado
    
    except dns.resolver.Timeout:
        resultado["status"] = "error"
        resultado["error"] = f"Timeout al consultar registros A de '{domain}'."
        return resultado
        
    except Exception as e:
        resultado["status"] = "error"
        resultado["error"] = f"Error inesperado consultando A: {str(e)}"
        return resultado

    #Consulta DNS tipo AAAA
    try:
        respuestas_aaaa = dns.resolver.resolve(domain, 'AAAA')
        for rdata in respuestas_aaaa:
            resultado["data"]["AAAA"].append(str(rdata.address))

    except dns.resolver.NoAnswer:
        print("No hay registros AAAA")
        pass

    except dns.resolver.NXDOMAIN:
        resultado["status"] = "error"
        resultado["error"] = f"El dominio '{domain}' no existe (NXDOMAIN) durante consulta AAAA."
        return resultado
    
    except dns.resolver.NoNameservers:
        resultado["status"] = "error"
        resultado["error"] = f"No se pudo contactar con los servidores DNS para '{domain}' (AAAA)."
        return resultado
    
    except dns.resolver.Timeout:
        resultado["status"] = "error"
        resultado["error"] = f"Timeout al consultar registros AAAA de '{domain}'."
        return resultado
    
    except Exception as e:
        resultado["status"] = "error"
        resultado["error"] = f"Error inesperado consultando AAAA: {str(e)}"
        return resultado

    # En caso de que ambas listas estén vacías
    if not resultado["data"]["A"] and not resultado["data"]["AAAA"]:
        resultado["status"] = "empty"
        resultado["error"] = "No se encontraron registros A ni AAAA para el dominio."

    return resultado

def get_mx_ns_records(domain):
    """Estudiante 2: Consulta registros MX y NS"""
    print(f"  [G1-E2] Consultando registros MX/NS para: {domain}")
    raise NotImplementedError("El módulo de registros MX/NS aún está en desarrollo por el Estudiante 2.")

def get_txt_soa_records(domain):
    """Estudiante 3: Consulta registros TXT y SOA"""
    print(f"  [G1-E3] Consultando registros TXT/SOA para: {domain}")
    raise NotImplementedError("El módulo de registros TXT/SOA aún está en desarrollo por el Estudiante 3.")