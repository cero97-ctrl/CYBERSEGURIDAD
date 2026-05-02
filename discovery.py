# Grupo 3: Descubrimiento de Hosts (3 estudiantes)
import datetime
import ipaddress
import subprocess
from scapy.all import IP, TCP, sr1

def ping_sweep(target_range: str, timeout: int = 10) -> dict:
    """
    Estudiante 1: Implementa un ping sweep utilizando el comando ping para identificar hosts activos en una red.

    Args:
        target_range (str): El rango de red en formato CIDR
        timeout (int): Timeout en ms para cada ping (default: 10 ms).
    
    Returns:
        Dict: Resultados de la auditoría, cumpliendo con el esquema definido en docs/schema_resultados.json.
    """
    resultado = {
        "modulo": "Discovery",
        "grupo": 3,
        "estudiante": "E1",
        "target": target_range,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "success",
        "data": {"hosts_activos": []},
        "error_message": None
    }
    #Verificar si el formato del rango es correcto
    try:
        red = ipaddress.ip_network(target_range, strict=False)
        for host in red.hosts():
            direccion = str(host)
            comando = ["ping", "-n", "1", "-w", str(timeout), direccion]
            respuesta = subprocess.run(comando, capture_output=True, text=True)
            if respuesta.returncode == 0:
                print(f"[+] Host encontrado en: {direccion}\n")
                resultado["data"]["hosts_activos"].append(direccion)
        # Si no se encontró ningún host activo, puedes dejar la lista vacía
    except Exception as e:
        resultado["status"] = "error"
        resultado["error_message"] = str(e)
    return resultado

def procesar_cidr(rango_cidr: str) -> dict:
    """
    Procesa un rango de red en formato CIDR y devuelve una lista de IPs válidas.

    Args:
        rango_cidr (str): El rango de red a procesar en notación CIDR (ej. '192.168.1.0/24').

    Returns:
        dict: Resultados siguiendo el esquema JSON definido.
    """
    resultados = {
        "modulo": "Discovery",
        "grupo": 3,
        "estudiante": "E2",
        "target": rango_cidr,
        "timestamp": datetime.datetime.now().isoformat(),
        "exito": False,
        "datos": [],
        "error_message": None
    }

    try:
        # strict=False permite procesar direcciones IP de host con máscaras de red
        red = ipaddress.ip_network(rango_cidr, strict=False)
        # Extraemos las IPs válidas (excluyendo la dirección de red y de broadcast)
        resultados["datos"] = [str(ip) for ip in red.hosts()]
        resultados["exito"] = True
        
    except ValueError as e:
        resultados["error_message"] = f"Formato CIDR inválido: {e}"
    except Exception as e:
        resultados["error_message"] = f"Error inesperado: {e}"

    return resultados

def ping_tcp_ack(target_range: str) -> dict:
    """
    Estudiante 3: Realiza un descubrimiento de hosts que responden con un paquete RST (TCP ACK Scan).
    Es necesario tener permisos de administrador.

    Args:
        target_range (str): El rango de red en formato CIDR (ej. '192.168.1.0/24').

    Returns:
        Dict[str, Any]: Resultados de la auditoría, cumpliendo con el esquema definido en docs/schema_resultados.json.
    """
    resultado = {
        "modulo": "Discovery",
        "grupo": 3,
        "estudiante": "E3",
        "target": target_range,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "success",
        "data": {"hosts_activos": []},
        "error_message": None
    }
    try:
        red = ipaddress.ip_network(target_range, strict=False)
        for host in red.hosts():
            pkt = IP(dst=str(host))/TCP(dport=80, flags="A")
            resp = sr1(pkt, timeout=1, verbose=0)
            if resp and resp.haslayer(TCP) and resp.getlayer(TCP).flags == 0x4:  # RST
                print(f"[+] Host activo (RST recibido): {host}")
                resultado["data"]["hosts_activos"].append(str(host))
    except Exception as e:
        resultado["status"] = "error"
        resultado["error_message"] = str(e)
    return resultado