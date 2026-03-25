#!/usr/bin/env python3
import os
import sys
import argparse
import json
import hashlib
import urllib.request
import urllib.error
import time
from datetime import datetime

# =========================
# Configuración mínima
# =========================
EXTENSIONES_PERMITIDAS = (
    ".html", ".css", ".js", ".php", ".py", ".java", ".sql",
    ".c", ".cpp", ".cu", ".h", ".json", ".xml", ".md", ".noema"
)

CARPETAS_EXCLUIDAS = {
    ".git", "node_modules", "vendor", "venv", "__pycache__",
    "modelo_entrenado", ".venv", "dist",
    "documentacion",  # <-- evitar folder documentacion (global)
}

LANG_MAP = {
    ".html": "html", ".css": "css", ".js": "js", ".php": "php",
    ".py": "python", ".java": "java", ".sql": "sql", ".c": "c",
    ".cpp": "cpp", ".cu": "cuda", ".h": "c", ".json": "json",
    ".xml": "xml", ".md": "markdown",
}

# =========================
# Progress Tracker
# =========================
class ProgressTracker:
    def __init__(self, total_tasks: int):
        self.total = total_tasks
        self.done = 0
        self.start_time = time.time()

    def increment(self, name: str = ""):
        self.done += 1
        elapsed = time.time() - self.start_time
        avg_time_per_task = elapsed / self.done
        remaining = self.total - self.done
        eta_sec = remaining * avg_time_per_task
        
        m, s = divmod(int(eta_sec), 60)
        h, m = divmod(m, 60)
        eta_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        
        # Formatear el nombre para que no rompa la consola si es muy largo
        name_clean = name[:30].ljust(30)
        
        sys.stdout.write(f"\r[IA Progress] {self.done}/{self.total} tareas | ETA: {eta_str} | Actual: {name_clean}")
        sys.stdout.flush()

    def finish(self):
        sys.stdout.write("\n")


def contar_tareas(ruta: str, exclude_root: set, _is_root: bool = True) -> int:
    """Cuenta cuántos archivos y carpetas válidos se procesarán con la IA."""
    count = 1  # 1 por el resumen de la carpeta en sí
    try:
        entradas = os.listdir(ruta)
    except Exception:
        return count

    for e in entradas:
        ruta_completa = os.path.join(ruta, e)
        if os.path.isfile(ruta_completa) and e.lower().endswith(EXTENSIONES_PERMITIDAS):
            count += 1
        elif os.path.isdir(ruta_completa):
            if e in CARPETAS_EXCLUIDAS:
                continue
            if _is_root and e in exclude_root:
                continue
            count += contar_tareas(ruta_completa, exclude_root, False)
            
    return count

# =========================
# IA (Ollama)
# =========================
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:7b"


def ollama_generate(prompt: str, ollama_url: str = DEFAULT_OLLAMA_URL, model: str = DEFAULT_MODEL, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ollama_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            j = json.loads(raw)
            return (j.get("response") or "").strip()
    except urllib.error.HTTPError as e:
        return f"[IA ERROR] HTTPError {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"[IA ERROR] URLError: {e.reason}"
    except Exception as e:
        return f"[IA ERROR] {e}"


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def resumir_archivo_con_ia(ruta_archivo: str, contenido: str, relpath: str, ollama_url: str, model: str) -> str:
    max_chars = 12000
    snippet = contenido[:max_chars]

    prompt = f"""
Eres un asistente que resume código para documentación interna.

Devuelve SOLO un resumen en español, conciso y útil, en 3 a 8 líneas.
NO uses Markdown.
NO uses viñetas con caracteres raros.
Evita florituras.

Ruta del archivo: {relpath}

Contenido (posiblemente recortado):
{snippet}
""".strip()

    return ollama_generate(prompt, ollama_url=ollama_url, model=model)


def resumir_carpeta_con_ia(nombre_carpeta: str, relpath: str, archivos_info: list, ollama_url: str, model: str) -> str:
    partes = []
    for a in archivos_info[:80]:
        s = (a.get("summary") or "").replace("\n", " ").strip()
        if len(s) > 300:
            s = s[:300] + "…"
        partes.append(f"- {a.get('path')}: {s}")

    contexto = "\n".join(partes)

    prompt = f"""
Eres un asistente que resume una carpeta de proyecto a partir de los resúmenes de sus archivos.

Devuelve SOLO un resumen en español, conciso y útil, en 3 a 8 líneas.
NO uses Markdown.
NO uses listas largas. Enfócate en propósito y componentes clave.

Carpeta: {relpath} (nombre: {nombre_carpeta})

Resúmenes de archivos:
{contexto}
""".strip()

    return ollama_generate(prompt, ollama_url=ollama_url, model=model)


# =========================
# Utilidades
# =========================
def parse_exclude_list(value: str) -> set[str]:
    if not value:
        return set()
    parts = [p.strip() for p in value.split(",")]
    return {p for p in parts if p}


def construir_mapa_directorios(ruta_raiz: str, excluir_root: set[str] | None = None) -> str:
    if excluir_root is None:
        excluir_root = set()

    lineas = []
    raiz_abs = os.path.abspath(ruta_raiz)
    lineas.append(raiz_abs)

    def interno(dir_path: str, prefijo: str = "", es_root: bool = False):
        try:
            entradas = sorted(os.listdir(dir_path))
        except Exception:
            return

        entradas_visibles = []
        for e in entradas:
            full = os.path.join(dir_path, e)

            if os.path.isdir(full) and e in CARPETAS_EXCLUIDAS:
                continue

            if es_root and os.path.isdir(full) and e in excluir_root:
                continue

            entradas_visibles.append(e)

        for i, entrada in enumerate(entradas_visibles):
            ruta_completa = os.path.join(dir_path, entrada)
            conector = "└── " if i == len(entradas_visibles) - 1 else "├── "
            lineas.append(prefijo + conector + entrada)
            if os.path.isdir(ruta_completa):
                extension = "    " if i == len(entradas_visibles) - 1 else "│   "
                interno(ruta_completa, prefijo + extension, es_root=False)

    interno(ruta_raiz, es_root=True)
    return "\n".join(lineas)


def generar_reporte_intercalado(
    ruta_raiz: str,
    nivel: int = 1,
    usar_ia: bool = False,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    cache: dict | None = None,
    rel_base: str | None = None,
    root_excludes: set[str] | None = None,
    _is_root: bool = False,
    progress: ProgressTracker | None = None
) -> str:
    
    if root_excludes is None:
        root_excludes = set()

    encabezado = "#" * nivel
    nombre_carpeta = os.path.basename(ruta_raiz) or ruta_raiz
    lineas = [f"{encabezado} {nombre_carpeta}"]

    if rel_base is None:
        rel_base = ruta_raiz

    relpath_carpeta = os.path.relpath(ruta_raiz, start=rel_base)
    if relpath_carpeta == ".":
        relpath_carpeta = os.path.basename(os.path.abspath(ruta_raiz))

    try:
        entradas = sorted(os.listdir(ruta_raiz))
    except Exception as e:
        lineas.append(f"Error listando la carpeta: {e}")
        return "\n".join(lineas)

    # --------
    # Archivos de este nivel
    # --------
    archivos_resumen_carpeta = [] 

    for entrada in entradas:
        ruta_completa = os.path.join(ruta_raiz, entrada)
        if os.path.isfile(ruta_completa) and entrada.lower().endswith(EXTENSIONES_PERMITIDAS):
            ext = os.path.splitext(entrada)[1].lower()
            lang = LANG_MAP.get(ext, "")
            lineas.append(f"**{entrada}**")

            try:
                with open(ruta_completa, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()
            except Exception as e:
                contenido = f"Error al leer el archivo: {e}"

            relpath_archivo = os.path.relpath(ruta_completa, start=rel_base)

            resumen_archivo = ""
            if usar_ia:
                if cache is None:
                    cache = {}
                key = "file:" + _sha1(relpath_archivo + "\n" + contenido[:12000])
                if key in cache:
                    resumen_archivo = cache[key]
                else:
                    resumen_archivo = resumir_archivo_con_ia(
                        ruta_archivo=ruta_completa,
                        contenido=contenido,
                        relpath=relpath_archivo,
                        ollama_url=ollama_url,
                        model=model
                    )
                    cache[key] = resumen_archivo

                if progress:
                    progress.increment(entrada)

                lineas.append(f"Resumen (IA): {resumen_archivo}")

                archivos_resumen_carpeta.append({
                    "path": relpath_archivo,
                    "name": entrada,
                    "ext": ext,
                    "summary": resumen_archivo
                })

            lineas.append(f"```{lang}")
            lineas.append(contenido)
            lineas.append("```")

    # Resumen IA de carpeta (si aplica)
    if usar_ia:
        if cache is None:
            cache = {}
        key = "dir:" + _sha1(relpath_carpeta + "\n" + json.dumps(archivos_resumen_carpeta, ensure_ascii=False))
        if key in cache:
            resumen_carpeta = cache[key]
        else:
            resumen_carpeta = resumir_carpeta_con_ia(
                nombre_carpeta=nombre_carpeta,
                relpath=relpath_carpeta,
                archivos_info=archivos_resumen_carpeta,
                ollama_url=ollama_url,
                model=model
            )
            cache[key] = resumen_carpeta

        if progress:
            progress.increment(f"Dir: {nombre_carpeta}")

        lineas.insert(1, f"Resumen de carpeta (IA): {resumen_carpeta}")

    # --------
    # Subcarpetas
    # --------
    for entrada in entradas:
        ruta_completa = os.path.join(ruta_raiz, entrada)

        if os.path.isdir(ruta_completa):
            if entrada in CARPETAS_EXCLUIDAS:
                continue

            if _is_root and entrada in root_excludes:
                continue

            lineas.append(
                generar_reporte_intercalado(
                    ruta_completa,
                    nivel + 1,
                    usar_ia=usar_ia,
                    ollama_url=ollama_url,
                    model=model,
                    cache=cache,
                    rel_base=rel_base,
                    root_excludes=root_excludes,
                    _is_root=False,
                    progress=progress
                )
            )

    return "\n".join(lineas)


def generar_reporte(
    ruta_origen: str,
    usar_ia: bool = False,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    exclude_root: set[str] | None = None
) -> str:
    
    if exclude_root is None:
        exclude_root = set()

    arbol = construir_mapa_directorios(ruta_origen, excluir_root=exclude_root)
    cache = {}
    
    progress = None
    if usar_ia:
        print("[INFO] Calculando archivos para estimar tiempo...")
        total_tareas = contar_tareas(ruta_origen, exclude_root)
        progress = ProgressTracker(total_tareas)

    intercalado = generar_reporte_intercalado(
        ruta_origen,
        usar_ia=usar_ia,
        ollama_url=ollama_url,
        model=model,
        cache=cache,
        rel_base=ruta_origen,
        root_excludes=exclude_root,
        _is_root=True,
        progress=progress
    )

    if progress:
        progress.finish()

    partes = []
    partes.append("# Reporte de proyecto\n")
    partes.append("## Estructura del proyecto\n")
    partes.append("```\n" + arbol + "\n```\n")
    partes.append("## Código (intercalado)\n")
    partes.append(intercalado)
    return "\n".join(partes)


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(
        description="Genera un reporte Markdown de una carpeta de código (árbol + contenidos)."
    )
    parser.add_argument("source_root", help="Carpeta origen a inspeccionar")
    parser.add_argument("dest_folder", help="Carpeta destino donde guardar el reporte")

    parser.add_argument(
        "-ia", "--ia",
        action="store_true",
        help="Si se indica, usa Ollama para resumir cada archivo y carpeta (en español)."
    )

    parser.add_argument(
        "--ollama-url",
        default=DEFAULT_OLLAMA_URL,
        help=f"URL del endpoint de Ollama (por defecto: {DEFAULT_OLLAMA_URL})"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modelo de Ollama (por defecto: {DEFAULT_MODEL})"
    )

    parser.add_argument(
        "--exclude-root",
        default="",
        help="Lista separada por comas de carpetas a excluir SOLO en la raíz del proyecto. Ej: build,docs,tmp"
    )

    args = parser.parse_args()

    source_root = os.path.abspath(args.source_root)
    dest_folder = os.path.abspath(args.dest_folder)

    if not os.path.isdir(source_root):
        print(f"[ERROR] La carpeta origen no existe o no es un directorio: {source_root}", file=sys.stderr)
        sys.exit(1)

    if os.path.basename(source_root.rstrip(os.sep)) in CARPETAS_EXCLUIDAS:
        print(f"[ERROR] La carpeta origen está excluida por configuración: {source_root}", file=sys.stderr)
        sys.exit(1)

    exclude_root = parse_exclude_list(args.exclude_root)

    os.makedirs(dest_folder, exist_ok=True)

    base_name = os.path.basename(source_root.rstrip(os.sep)) or "reporte"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_name = f"{base_name}_{timestamp}.md"
    out_path = os.path.join(dest_folder, out_name)

    try:
        contenido = generar_reporte(
            source_root,
            usar_ia=bool(args.ia),
            ollama_url=args.ollama_url,
            model=args.model,
            exclude_root=exclude_root
        )
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(contenido)
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Proceso cancelado por el usuario.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] No se pudo generar o guardar el reporte: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"[OK] Reporte generado: {out_path}")
    if exclude_root:
        print(f"[OK] Excluyendo en raíz: {', '.join(sorted(exclude_root))}")
    if args.ia:
        print(f"[OK] IA activada: modelo={args.model} url={args.ollama_url}")


if __name__ == "__main__":
    main()