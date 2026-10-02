"""Genera data/registros/solo_por_cita.json: documentos que solo se recuperan si la consulta los nombra.

    python src/indexacion/solo_por_cita.py                  # base = manifest de e8e7e58 (corpus v2)
    python src/indexacion/solo_por_cita.py --base <commit>

Motivo (docs/INDEXACION.md secciones 13 y 14): el corpus v3 agrego 279 sentencias
(242 SU 2020-2026 y 37 hitos) y 96 normas. En el hibrido desplazan a los codigos y
leyes que fundamentan la mayoria de las preguntas, y solo ayudan cuando la pregunta
nombra la sentencia. Los documentos de este registro se quitan de las ramas BM25 y
densa salvo que `citations.extract` de la consulta encuentre su cuerpo canonico
(recuperacion/retriever.py). El registro se versiona; este script solo deja
constancia de como se armo (necesita el historial de git, el runtime no).

Grupos (SYNTAX_FILTRO_CITA elige cuales se aplican): `sentencias` = tipo sentencia
nuevo frente a la base; `normas` = el resto de documentos nuevos.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

BASE_V2 = "e8e7e58"  # ultimo commit con el corpus v2 (213 documentos)


def doc_ids_en(commit: str) -> set[str]:
    texto = subprocess.run(["git", "show", f"{commit}:corpus_manifest.json"], cwd=config.ROOT,
                           capture_output=True, check=True).stdout.decode("utf-8")
    return {d["doc_id"] for d in json.loads(texto)["documentos"]}


def tipos_por_doc() -> dict[str, str]:
    tipos: dict[str, str] = {}
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        for linea in f:
            c = json.loads(linea)
            tipos.setdefault(c["doc_id"], c["tipo"])
    return tipos


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default=BASE_V2, help="commit cuyo manifest define el corpus base")
    args = ap.parse_args()
    base = doc_ids_en(args.base)
    actuales = [d["doc_id"] for d in json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]]
    tipos = tipos_por_doc()
    nuevos = sorted(d for d in actuales if d not in base)
    registro = {
        "_comentario": "Generado por src/indexacion/solo_por_cita.py; no editar a mano. "
                       "Documentos que solo se recuperan si la consulta los nombra (docs/INDEXACION.md 14).",
        "base": args.base,
        "sentencias": [d for d in nuevos if tipos.get(d) == "sentencia"],
        "normas": [d for d in nuevos if tipos.get(d) != "sentencia"],
    }
    config.SOLO_POR_CITA_PATH.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")
    print(f"{config.SOLO_POR_CITA_PATH.relative_to(config.ROOT)}: base {args.base} ({len(base)} docs), "
          f"{len(registro['sentencias'])} sentencias y {len(registro['normas'])} normas solo por cita")


if __name__ == "__main__":
    main()
