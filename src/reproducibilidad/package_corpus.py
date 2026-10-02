"""Empaqueta el corpus y el indice congelados para publicarlos (enunciado, secc. 9 y 9.3).

    python src/reproducibilidad/package_corpus.py                       # LICENSE en ../LICENSE
    python src/reproducibilidad/package_corpus.py --licencia <ruta> [--nombre Syntax-corpus-v4]
    python src/reproducibilidad/package_corpus.py --sin-licencia --nombre <snapshot>   # congelado interno

Contenido del zip (raiz `<nombre>/`): corpus/ (los .txt del manifest), indice/ (index.faiss,
chunks.jsonl, bm25/, indice_info.json, resumen_indice.json), LICENSE y una copia de
corpus_manifest.json (el mismo archivo versionado en el repo). Antes de escribir comprueba que
corpus/ e indice/ sean los congelados (verificar_corpus.py) y que el indice sea coherente
(config.verificar_indice). El zip es determinista (orden fijo y fecha fija en cada entrada): el
mismo contenido da el mismo sha256, que se anota en CORPUS.md. Sale en data_corpus/ (en .gitignore).
Solo stdlib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

FECHA_FIJA = (2026, 10, 3, 0, 0, 0)
ARCHIVOS_INDICE = ("index.faiss", "chunks.jsonl", "indice_info.json", "resumen_indice.json")


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def entradas(licencia: Path | None) -> list[tuple[str, Path]]:
    """(ruta dentro del zip sin la raiz, archivo local), en orden fijo."""
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    salida = ([("LICENSE", licencia)] if licencia else []) + [("corpus_manifest.json", config.MANIFEST_PATH)]
    for d in sorted(manifest["documentos"], key=lambda d: d["doc_id"]):
        salida.append((f"corpus/{d['doc_id']}.txt", config.CORPUS_TEXTOS / f"{d['doc_id']}.txt"))
    for nombre in ARCHIVOS_INDICE:
        salida.append((f"indice/{nombre}", config.INDICE_DIR / nombre))
    for f in sorted(p for p in config.BM25_DIR.rglob("*") if p.is_file()):
        salida.append((f"indice/bm25/{f.relative_to(config.BM25_DIR).as_posix()}", f))
    return salida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--licencia", type=Path, default=config.ROOT.parent / "LICENSE",
                    help="LICENSE del corpus (CC-BY-4.0); por defecto ../LICENSE")
    ap.add_argument("--nombre", default="Syntax-corpus-v4", help="nombre del zip y de su carpeta raiz")
    ap.add_argument("--sin-verificar", action="store_true", help="no correr verificar_corpus.py (solo pruebas)")
    ap.add_argument("--sin-licencia", action="store_true",
                    help="snapshot interno para reproducir (no publicable): el zip va sin LICENSE")
    args = ap.parse_args()

    if args.sin_licencia:
        args.licencia = None
    elif not args.licencia.is_file():
        print(f"ERROR: no esta el LICENSE en {args.licencia}; pasar --licencia <ruta>", file=sys.stderr)
        return 1
    config.verificar_indice()
    if not args.sin_verificar:
        r = subprocess.run([sys.executable, str(config.ROOT / "src" / "reproducibilidad" / "verificar_corpus.py")])
        if r.returncode != 0:
            print("ERROR: corpus/ o indice/ no son los congelados; no se empaqueta", file=sys.stderr)
            return 1
    lista = entradas(args.licencia)
    faltan = [str(local) for _, local in lista if not local.is_file()]
    if faltan:
        print(f"ERROR: faltan {len(faltan)} archivos, p. ej. {faltan[:3]}", file=sys.stderr)
        return 1

    destino = config.CORPUS_DIR / f"{args.nombre}.zip"
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for ruta, local in lista:
            info = zipfile.ZipInfo(f"{args.nombre}/{ruta}", date_time=FECHA_FIJA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with local.open("rb") as fuente, z.open(info, "w", force_zip64=True) as dst:
                for bloque in iter(lambda: fuente.read(1 << 20), b""):
                    dst.write(bloque)
    sha = sha256_archivo(destino)
    print(f"{destino.relative_to(config.ROOT).as_posix()}: {len(lista)} archivos, "
          f"{destino.stat().st_size / 1e6:.1f} MB")
    print(f"sha256 {sha}  (anotar en CORPUS.md junto al enlace publico)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
