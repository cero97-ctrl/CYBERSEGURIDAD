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
    raise NotImplementedError("El módulo de registros A/AAAA aún está en desarrollo por el Estudiante 1.")

def get_mx_ns_records(domain):
    """Estudiante 2: Consulta registros MX y NS"""
    print(f"  [G1-E2] Consultando registros MX/NS para: {domain}")
    raise NotImplementedError("El módulo de registros MX/NS aún está en desarrollo por el Estudiante 2.")

def get_txt_soa_records(domain):
    """Estudiante 3: Consulta registros TXT y SOA"""
    print(f"  [G1-E3] Consultando registros TXT/SOA para: {domain}")
    raise NotImplementedError("El módulo de registros TXT/SOA aún está en desarrollo por el Estudiante 3.")