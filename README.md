# lightgoldenrodyellow.py

Generador ligero de reportes Markdown para proyectos de código.

Este repositorio contiene un script en Python (`lightgoldenrodyellow.py`) que recorre una carpeta de proyecto y genera un **reporte en Markdown** con:

- Un **árbol de directorios** estilo `tree` (con exclusiones configurables).
- El **código intercalado**: incluye el contenido de cada archivo permitido dentro de bloques Markdown con el lenguaje adecuado.

Ideal para:
- Documentar proyectos rápidamente.
- Compartir el estado de un repositorio (estructura + contenido) en un único `.md`.
- Preparar material para revisión, auditoría o IA (contexto completo de un proyecto).

---

## Características

- ✅ Árbol de directorios con conectores (`├──`, `└──`) y exclusión de carpetas comunes.
- ✅ Inserta el contenido de archivos permitidos en bloques de código Markdown con *syntax highlighting*.
- ✅ Configuración mínima: extensiones permitidas, carpetas excluidas y mapa de lenguajes.
- ✅ Funciona con proyectos pequeños/medianos sin dependencias externas.

---

## Requisitos

- Python 3.8+ (recomendado)
- Sin dependencias adicionales.

---

## Uso

Ejecuta el script indicando:

1) carpeta origen a inspeccionar  
2) carpeta destino donde guardar el reporte

```bash
python3 lightgoldenrodyellow.py /ruta/al/proyecto /ruta/destino
````

Ejemplo:

```bash
python3 lightgoldenrodyellow.py ./mi_proyecto ./reportes
```

Salida típica:

```
[OK] Reporte generado: /ruta/destino/mi_proyecto_20260114091530.md
```

---

## Qué incluye el reporte

El `.md` generado tendrá esta estructura:

* `# Reporte de proyecto`
* `## Estructura del proyecto` (árbol completo)
* `## Código (intercalado)` (por carpetas y archivos)

Los archivos se incluyen solo si su extensión está en `EXTENSIONES_PERMITIDAS`, y las carpetas se omiten si están en `CARPETAS_EXCLUIDAS`.

---

## Configuración

Dentro del script puedes ajustar:

### Extensiones permitidas

```python
EXTENSIONES_PERMITIDAS = (
    ".html", ".css", ".js", ".php", ".py", ".java", ".sql",
    ".c", ".cpp", ".cu", ".h", ".json", ".xml", ".md"
)
```

### Carpetas excluidas

```python
CARPETAS_EXCLUIDAS = {
    ".git", "node_modules", "vendor", "venv", "__pycache__",
    "modelo_entrenado", ".venv","dist"
}
```

### Mapeo de lenguaje (Markdown fences)

```python
LANG_MAP = {
  ".py": "python",
  ".js": "js",
  ".cpp": "cpp",
  ...
}
```

---

## Notas y recomendaciones

* Si tu proyecto contiene archivos grandes, el reporte puede crecer mucho.
* Para evitar incluir secretos (tokens, claves), revisa el contenido antes de compartir el `.md`.
* Si necesitas excluir archivos concretos (por patrón), se puede ampliar fácilmente.

---

## Licencia

Añade aquí la licencia que prefieras (MIT, Apache-2.0, GPL, etc.).
Si no tienes una aún, una opción habitual para scripts utilitarios es **MIT**.

---



