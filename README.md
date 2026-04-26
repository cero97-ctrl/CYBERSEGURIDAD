# Information Security Auditing Suite

This project is a modular auditing tool developed collaboratively by the 13 students of the **Information Security** course.

## 🚀 Parallel Work and Collaboration Guide

To maximize efficiency and avoid bottlenecks, the project uses a decoupled architecture. This allows the 4 groups to work simultaneously without depending on each other's progress.

### 1. Module Independence
Each group has its own development file in the `modulos/` folder.
- **Grupo 1 (DNS):** `modulos/dns_recon.py`
- **Grupo 2 (OSINT):** `modulos/osint.py`
- **Grupo 3 (Discovery):** `modulos/discovery.py`
- **Grupo 4 (Scanning):** `modulos/scanning.py`

**Golden Rule:** It is strictly forbidden to modify `auditoria.py` or other groups' files. Your work is limited exclusively to your assigned file.

### 2. The Data Contract (The Key to Parallelism)
You don't need to wait for the "Reconnaissance" groups to finish for your "Scanning" code to work. Integration does not depend on others' code, but on **compliance with the output contract**.
- All functions must return a dictionary that complies with the schema defined in `docs/schema_resultados.json`.
- As long as you respect this format, the main orchestrator and the future reporting module will work correctly.

### 3. Unit Tests
You can (and should) test your functionality in isolation using known test targets (e.g., `google.com` or `8.8.8.8`).
```bash
# Example: Group 4 can test its scanner without waiting for Group 1
python auditoria.py 8.8.8.8 --scan 80,443
```

## 🛠️ Configuración del Entorno

1. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
2. (Opcional pero recomendado) Instala la librería de validación para verificar tus contratos:
   ```bash
   pip install jsonschema
   ```

## 📝 Estándares de Código

Para asegurar la calidad profesional de la suite, cada entrega debe cumplir con:
1. **Type Hinting:** Todas las funciones deben declarar tipos de entrada y salida.
2. **Docstrings:** Uso obligatorio del estilo Google para documentar argumentos y retornos.
3. **Manejo de Errores:** Uso de bloques `try-except` para prevenir caídas del sistema.
4. **Validación:** Antes de realizar un `push`, verifica que tu retorno pase la validación de `auditoria.py`.

## 🔄 Flujo de Trabajo (Git)

Para sincronizar tu trabajo, utiliza el script proporcionado:
```bash
python3 git_update.py "Descripción breve de tu cambio"
```
Esto realizará el commit de tus cambios, descargará las actualizaciones de tus compañeros y subirá tu trabajo al repositorio de forma segura.

---
*Propiedad del Curso de Seguridad Informática - Prof. César Rodríguez*