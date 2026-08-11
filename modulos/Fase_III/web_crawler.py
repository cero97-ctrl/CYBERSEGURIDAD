import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class WebCrawler:
    """
    Grupo 1: Módulo de Rastreo y Mapeo Web (Crawler & Fuzzer).
    Responsable de mapear la estructura, buscar directorios y extraer datos.
    """
    def __init__(self, target_url: str):
        # Asegurar que el target tenga el esquema HTTP/HTTPS
        if not target_url.startswith("http"):
            self.target_url = f"http://{target_url}"
        else:
            self.target_url = target_url
            
        self.session = requests.Session()
        # Headers básicos para evitar ser bloqueado de inmediato
        self.session.headers.update({"User-Agent": "Auditoria-Python-Student-Bot/1.0"})
        self.response = None
        self.html = None

    def _fetch(self):
        """Realiza la petición GET y guarda la respuesta y el texto."""
        try:
            self.response = self.session.get(self.target_url, timeout=10)
            self.response.raise_for_status()  # Lanza excepción si hay error HTTP
            self.html = self.response.text
        except Exception as e:
            self.html = None
            self.response = None
            raise e

    def crawl_links(self) -> List[str]:
        """
        (Estudiante 1) Navega por la página y extrae todos los enlaces (href).
        """
        if not self.html:
            return []

        # Importamos urljoin localmente
        from urllib.parse import urljoin

        soup = BeautifulSoup(self.html, 'html.parser')
        enlaces = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            url_completa = urljoin(self.target_url, href)
            # Solo guardamos enlaces HTTP/HTTPS
            if url_completa.startswith(('http://', 'https://')):
                enlaces.add(url_completa)

        return list(enlaces)

    def brute_force_directories(self, wordlist: List[str]) -> List[str]:
        """
        (Estudiante 2) Busca directorios ocultos usando un diccionario.
        """
        encontrados = []
        base = self.target_url.rstrip('/')

        for palabra in wordlist:
            url = f"{base}/{palabra}"
            try:
                resp = self.session.get(url, timeout=5)
                if resp.status_code in (200, 403):
                    encontrados.append(url)

            except Exception:
                # Si da error de conexión, simplemente ignoramos esa palabra
                continue

        return encontrados


    def extract_sensitive_data(self) -> Dict[str, List[str]]:
        """
        (Estudiante 3) Extrae correos, comentarios HTML y scripts JS de la respuesta.
        """
        datos = {
            "emails": [],
            "html_comments": [],
            "js_scripts": [],
            "meta_tags": []
        }

        if not self.html:
            return datos

        # 1. Correos electrónicos
        patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        datos["emails"] = re.findall(patron_email, self.html)

        # 2. Comentarios HTML
        from bs4 import Comment
        soup = BeautifulSoup(self.html, 'html.parser')
        comentarios = soup.find_all(string=lambda texto: isinstance(texto, Comment))
        datos["html_comments"] = [str(c).strip() for c in comentarios]

        # 3. Scripts JS (etiquetas <script>)
        from urllib.parse import urljoin  # también lo usamos aquí
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src')
            if src:
                # Script externo: guardamos la URL absoluta
                url_script = urljoin(self.target_url, src)
                datos["js_scripts"].append(url_script)
            else:
                # Script inline: guardamos el contenido (limitado a 200 caracteres)
                contenido = script.string
                if contenido:
                    datos["js_scripts"].append(f"inline: {contenido[:200]}...")
        
        metas = soup.find_all('meta')
        for meta in metas:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                datos["meta_tags"].append(f"{name}: {content}")

        return datos

    def run(self) -> Dict[str, Any]:
        """
        Orquesta las funciones del Grupo 1 y retorna los resultados formateados.
        """
        resultados_crawler = {}
        
        try:
            self._fetch()  # Obtener la página inicial

            resultados_crawler['links'] = self.crawl_links()
            resultados_crawler['directories'] = self.brute_force_directories(['admin', 'backup', 'robots.txt', 'login', 'config', 'wp-admin', 'secret'])
            resultados_crawler['sensitive'] = self.extract_sensitive_data()
        except Exception as e:
            return {
                "modulo": "WEB_CRAWLER",
                "estudiante": "Grupo 1",
                "target": self.target_url,
                "status": "error",
                "error_message": str(e),
                "data": {}
            }

        return {
            "modulo": "WEB_CRAWLER",
            "estudiante": "Grupo 1",
            "target": self.target_url,
            "status": "success",
            "data": resultados_crawler
        }

if __name__ == "__main__":
    import json

    print("[*] Iniciando prueba local del Crawler...")
    crawler = WebCrawler("http://testphp.vulnweb.com")
    resultado = crawler.run()

    print("\n" + "="*60)
    print("RESULTADOS DEL CRAWLER")
    print("="*60)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
    print("="*60)