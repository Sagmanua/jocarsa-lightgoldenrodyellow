
# lightgoldenrodyellow.py

Generador ligero de reportes Markdown para proyectos de código.

Este repositorio contiene un script en Python (`lightgoldenrodyellow.py`) que recorre una carpeta de proyecto y genera un **reporte en Markdown** con:

* Un **árbol de directorios** estilo `tree` (con exclusiones configurables).
* El **código intercalado**: incluye el contenido de cada archivo permitido dentro de bloques Markdown con el lenguaje adecuado.
* (Opcional) **Resúmenes automáticos con IA local** usando Ollama y el modelo `qwen2.5-coder:7b`.

Ideal para:

* Documentar proyectos rápidamente.
* Compartir el estado de un repositorio (estructura + contenido) en un único `.md`.
* Preparar material para revisión, auditoría o IA (contexto completo de un proyecto).
* Generar documentación técnica enriquecida automáticamente.

---

## Características

* ✅ Árbol de directorios con conectores (`├──`, `└──`).
* ✅ Exclusión automática de carpetas comunes y de `documentacion`.
* ✅ Inserta el contenido de archivos permitidos en bloques Markdown con *syntax highlighting*.
* ✅ Opción `-ia` para generar:

  * Resumen en español de cada archivo.
  * Resumen en español de cada carpeta.
* ✅ Uso de modelo local (`qwen2.5-coder:7b`) vía Ollama.
* ✅ Sin dependencias externas obligatorias (modo normal).
* ✅ Caché interna para evitar repetir llamadas IA innecesarias.

---

## Requisitos

### Modo normal (sin IA)

* Python 3.8+
* Sin dependencias adicionales.

### Modo IA (`-ia`)

* Python 3.8+
* Ollama instalado y ejecutándose.
* Modelo descargado:

```bash
ollama pull qwen2.5-coder:7b
```

Servidor activo en:

```
http://localhost:11434
```

---

## Uso

Ejecuta el script indicando:

1. Carpeta origen a inspeccionar
2. Carpeta destino donde guardar el reporte

### Modo estándar (sin IA)

```bash
python3 lightgoldenrodyellow.py /ruta/al/proyecto /ruta/destino
```

Ejemplo:

```bash
python3 lightgoldenrodyellow.py ./mi_proyecto ./reportes
```

---

### Modo con IA (resúmenes automáticos)

```bash
python3 lightgoldenrodyellow.py /ruta/al/proyecto /ruta/destino -ia
```

Ejemplo:

```bash
python3 lightgoldenrodyellow.py ./mi_proyecto ./reportes -ia
```

Salida típica:

```
[OK] Reporte generado: /ruta/destino/mi_proyecto_20260114091530.md
[OK] IA activada: modelo=qwen2.5-coder:7b url=http://localhost:11434/api/generate
```

---

### Opciones avanzadas

Puedes personalizar el endpoint o modelo:

```bash
python3 lightgoldenrodyellow.py ./mi_proyecto ./reportes -ia \
  --ollama-url http://localhost:11434/api/generate \
  --model qwen2.5-coder:7b
```

---

## Qué incluye el reporte

El `.md` generado tendrá esta estructura:

* `# Reporte de proyecto`
* `## Estructura del proyecto`
* `## Código (intercalado)`

Si se usa `-ia`, además incluirá:

* `Resumen de carpeta (IA)` debajo de cada encabezado de carpeta.
* `Resumen (IA)` antes del bloque de código de cada archivo.

Los resúmenes:

* Están en español.
* Son concisos (3–8 líneas).
* No usan Markdown complejo.
* Están orientados a documentación técnica interna.

---

## Exclusiones automáticas

El script excluye automáticamente:

```
.git
node_modules
vendor
venv
__pycache__
modelo_entrenado
.venv
dist
documentacion
```

> La carpeta `documentacion` no se analiza ni se incluye en el reporte.

---

## Configuración

Dentro del script puedes ajustar:

### Extensiones permitidas

```python
EXTENSIONES_PERMITIDAS = (
    ".html", ".css", ".js", ".php", ".py", ".java", ".sql",
    ".c", ".cpp", ".cu", ".h", ".json", ".xml", ".md", ".noema"
)
```

---

### Carpetas excluidas

```python
CARPETAS_EXCLUIDAS = {
    ".git", "node_modules", "vendor", "venv", "__pycache__",
    "modelo_entrenado", ".venv", "dist", "documentacion"
}
```

---

### Mapeo de lenguaje (Markdown fences)

```python
LANG_MAP = {
  ".py": "python",
  ".js": "js",
  ".cpp": "cpp",
  ".cu": "cuda",
  ...
}
```

---

## Notas y recomendaciones

* Si tu proyecto contiene archivos grandes, el reporte puede crecer considerablemente.
* En modo `-ia`, el tiempo de generación aumentará proporcionalmente al número de archivos.
* Revisa siempre el `.md` antes de compartirlo si el proyecto contiene:

  * Tokens
  * Claves privadas
  * Credenciales
* Puedes ampliar fácilmente el script para:

  * Excluir archivos por patrón.
  * Generar solo resúmenes sin código.
  * Crear documentación técnica automática para clientes.

---

## Casos de uso interesantes

* Preparar contexto completo para otro modelo LLM.
* Crear snapshots documentales versionadas.
* Auditoría técnica rápida.
* Documentación automática de proyectos legacy.
* Exportar proyectos docentes para análisis estructural.

---

## Licencia

Añade aquí la licencia que prefieras (MIT, Apache-2.0, GPL, etc.).
Si no tienes una aún, una opción habitual para scripts utilitarios es **MIT**.
