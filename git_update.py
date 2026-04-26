#!/usr/bin/env python3
import subprocess
import os
import sys

def run_cmd(cmd_list, check=True):
    """Ejecuta un comando de sistema de forma segura (sin shell)."""
    return subprocess.run(cmd_list, check=check, capture_output=True, text=True)

def main():
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if not os.path.exists("./update_repo.sh"):
        print(f"Error: update_repo.sh no encontrado en {script_dir}")
        sys.exit(1)

    # Verificar que estamos en un repositorio git válido
    repo_check = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], check=False)
    if repo_check.returncode != 0:
        print(f"Error: El directorio {script_dir} no es un repositorio Git válido.")
        sys.exit(1)

    # Detectar rama actual
    try:
        branch = run_cmd(["git", "symbolic-ref", "--short", "HEAD"]).stdout.strip()
    except subprocess.CalledProcessError:
        branch = "main"

    print(f"[*] Iniciando actualización en rama: {branch}")

    # Guardar cambios locales (WIP)
    run_cmd(["git", "add", "-A"])
    staged = run_cmd(["git", "diff", "--staged", "--quiet"], check=False)
    
    if staged.returncode != 0:
        msg = sys.argv[1] if len(sys.argv) > 1 else "WIP: guardar cambios antes de pull"
        print(f"[*] Committing: {msg}")
        run_cmd(["git", "commit", "-m", msg])
    else:
        print("[*] No hay cambios locales para guardar.")

    # Ejecutar el script de sincronización
    print("[*] Ejecutando script de sincronización bash...")
    try:
        # Se omite capture_output para permitir que bash imprima directo a consola
        subprocess.run(["bash", "./update_repo.sh", "--remote", "origin", "--branch", branch, "--push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error: La sincronización falló (código de salida: {e.returncode})")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()