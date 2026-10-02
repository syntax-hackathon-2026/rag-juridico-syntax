"""Comprueba que corpus/ e indice/ locales son identicos a los congelados (misma salida en cualquier maquina).

  1. sha256 de cada data_corpus/corpus/<doc_id>.txt contra corpus_manifest.json.
  2. sha256 de data_corpus/indice/chunks.jsonl y version del segmentador contra
     data/registros/hashes_esperados.json (el segmentador es determinista: mismo corpus -> mismos fragmentos).

exit 1 si algo difiere: NO reconstruir con otro corpus, traer el corpus congelado (enlace publico) o
corregir el parseo. Ejecutar despues de segmentar/indexar y antes de evaluar o entregar.

  python src/reproducibilidad/verificar_corpus.py               # verificar
  python src/reproducibilidad/verificar_corpus.py --actualizar  # congelar los hashes actuales (solo una maquina)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

HASHES_PATH = config.ROOT / "data" / "registros" / "hashes_esperados.json"


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def version_segmentador() -> str | None:
    """Version escrita por segmentar.py (existe antes de indexar); indice_info.json como respaldo."""
    for ruta in (config.RESUMEN_INDICE_PATH, config.INDICE_INFO_PATH):
        if ruta.is_file():
            version = json.loads(ruta.read_text(encoding="utf-8")).get("version_segmentador")
            if version:
                return version
    return None


def actuales() -> dict:
    return {"version_segmentador": version_segmentador(),
            "n_documentos": len(list(config.CORPUS_TEXTOS.glob("*.txt"))),
            "sha256_chunks": sha256_archivo(config.CHUNKS_PATH)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--actualizar", action="store_true", help="escribir data/registros/hashes_esperados.json con lo local")
    args = ap.parse_args()

    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    errores: list[str] = []
    for d in manifest["documentos"]:
        ruta = config.CORPUS_TEXTOS / f"{d['doc_id']}.txt"
        if not ruta.is_file():
            errores.append(f"{d['doc_id']}: falta {ruta.name}")
        elif sha256_archivo(ruta) != d["sha256"]:
            errores.append(f"{d['doc_id']}: el texto local difiere del congelado en el manifest")
    print(f"corpus/: {len(manifest['documentos']) - len(errores)}/{len(manifest['documentos'])} "
          f"documentos identicos al manifest")

    if not config.CHUNKS_PATH.is_file():
        errores.append("falta indice/chunks.jsonl (correr src/indexacion/segmentar.py)")
    else:
        hoy = actuales()
        if args.actualizar:
            if errores:
                print("No se congela con un corpus que no coincide con el manifest:")
                print("\n".join(f"  - {e}" for e in errores))
                return 1
            HASHES_PATH.write_text(json.dumps(hoy, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"Congelado en {HASHES_PATH.relative_to(config.ROOT)}: {hoy['sha256_chunks'][:16]}...")
            return 0
        if not HASHES_PATH.is_file():
            errores.append("falta data/registros/hashes_esperados.json (correr con --actualizar en la maquina de referencia)")
        else:
            esperado = json.loads(HASHES_PATH.read_text(encoding="utf-8"))
            for k, v in hoy.items():
                if esperado.get(k) != v:
                    errores.append(f"chunks: {k} local {str(v)[:16]} != congelado {str(esperado.get(k))[:16]}")
            if not [e for e in errores if e.startswith("chunks")]:
                print(f"indice/chunks.jsonl: identico al congelado ({hoy['sha256_chunks'][:16]}...)")

    if errores:
        print("\nNO REPRODUCIBLE:")
        print("\n".join(f"  - {e}" for e in errores[:40]))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
