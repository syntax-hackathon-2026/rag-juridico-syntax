"""Construye el indice a partir de data_corpus/indice/chunks.jsonl (salida de segmentar.py).

    python src/indexacion/construir_indice.py              # BM25 + denso (bge-m3) + manifest
    python src/indexacion/construir_indice.py --solo-bm25  # sin encoder (iterar sin GPU)
    SYNTAX_DEVICE=cuda python src/indexacion/construir_indice.py --batch 64
    python src/indexacion/construir_indice.py --particion 2/3 --batch 16  # solo el trozo 2 de 3

Escribe en data_corpus/indice/:
  - bm25/          indice bm25s sobre retrieval_text (tokenizador de recuperacion/lexico.py)
  - index.faiss    IndexFlatIP exacto con los vectores normalizados de bge-m3; la fila i
                   es la linea i de chunks.jsonl (config.verificar_indice lo comprueba)
  - indice_info.json  encoder + revision, dimension, n, sha256 de chunks.jsonl, device...

--particion i/n: codifica solo los fragmentos del trozo i, que son las claves en la posicion i-1 (mod n) de la
lista ordenada de todas las claves (trozos disjuntos e independientes de la cache local) y que aun no estan en cache y escribe shards en la cache, sin
construir index.faiss ni tocar el manifest. Varias personas corren trozos distintos, juntan
sus cache_emb/ en una carpeta y una corrida final sin --particion arma el indice desde cache.

Los vectores se guardan tambien en data_corpus/cache_emb/<modelo>/ con clave = sha256
del retrieval_text: al agregar documentos solo se codifican los fragmentos nuevos o
cambiados, y una corrida interrumpida retoma donde quedo. Siempre en fp32 (las
consultas en vivo tambien): fp16 cambiaria el ranking entre maquinas.

Al final actualiza corpus_manifest.json: n_fragmentos por documento y en la raiz, y
sha256 del .txt si cambio. No toca n_articulos ni agrega/borra documentos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from recuperacion import lexico  # noqa: E402

SHARD = 512  # vectores por archivo de cache (cada shard escrito = progreso guardado)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cargar_chunks() -> list[dict]:
    if not config.CHUNKS_PATH.is_file():
        raise SystemExit(f"No existe {config.CHUNKS_PATH}; correr antes src/indexacion/segmentar.py")
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        chunks = [json.loads(l) for l in f if l.strip()]
    ids = [c["chunk_id"] for c in chunks]
    if len(ids) != len(set(ids)):
        raise SystemExit("chunk_id repetidos en chunks.jsonl; volver a segmentar")
    return chunks


# --- BM25 -------------------------------------------------------------------------

def construir_bm25(chunks: list[dict]) -> dict:
    import bm25s

    t0 = time.time()
    tokens = [lexico.tokenizar(c["retrieval_text"]) for c in chunks]
    params = {"k1": 1.5, "b": 0.75, "method": "lucene"}
    indice = bm25s.BM25(**params)
    indice.index(tokens, show_progress=False)
    indice.save(str(config.BM25_DIR))
    print(f"BM25: {len(chunks)} fragmentos, vocabulario {len(indice.vocab_dict)}, {time.time() - t0:.1f}s")
    return {**params, "tokenizador": lexico.VERSION, "vocabulario": len(indice.vocab_dict)}


# --- denso ------------------------------------------------------------------------

def _dir_cache() -> Path:
    slug = config.ENCODER_MODEL.replace("/", "__") + "@" + config.ENCODER_REVISION[:12]
    return config.EMB_CACHE_DIR / slug


def cargar_cache() -> dict[str, np.ndarray]:
    cache: dict[str, np.ndarray] = {}
    for shard in sorted(_dir_cache().glob("*.npz")):
        datos = np.load(shard)
        cache.update(zip(datos["claves"].tolist(), datos["vectores"]))
    return cache


def guardar_shard(claves: list[str], vectores: np.ndarray) -> None:
    d = _dir_cache()
    d.mkdir(parents=True, exist_ok=True)
    nombre = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".npz"
    np.savez(d / nombre, claves=np.array(claves), vectores=vectores.astype(np.float32))


def cargar_encoder(device: str):
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(config.ENCODER_MODEL, revision=config.ENCODER_REVISION, device=device)
    modelo.max_seq_length = config.ENCODER_MAX_SEQ
    return modelo


def construir_denso(chunks: list[dict], batch: int, particion: tuple[int, int] | None = None) -> dict | None:
    import faiss

    device = config.resolver_device()
    claves = [sha256_bytes(c["retrieval_text"].encode("utf-8")) for c in chunks]
    cache = cargar_cache()
    faltan = sorted({k for k in claves if k not in cache})
    print(f"Denso: {len(chunks)} fragmentos, {len(chunks) - len(faltan)} en cache, "
          f"{len(faltan)} por codificar ({config.ENCODER_MODEL}, device={device})")
    if particion:
        i, n = particion
        trozo = set(sorted(set(claves))[i - 1::n])  # sobre todas las claves: igual en cualquier maquina
        faltan = [k for k in faltan if k in trozo]
        print(f"Particion {i}/{n}: {len(faltan)} fragmentos de este trozo")
    if faltan:
        texto_de = {k: c["retrieval_text"] for k, c in zip(claves, chunks)}
        modelo = cargar_encoder(device)
        t0 = time.time()
        for i in range(0, len(faltan), SHARD):
            grupo = faltan[i:i + SHARD]
            vecs = modelo.encode([texto_de[k] for k in grupo], batch_size=batch,
                                 normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False).astype(np.float32)
            guardar_shard(grupo, vecs)
            cache.update(zip(grupo, vecs))
            hechos = i + len(grupo)
            ritmo = hechos / (time.time() - t0)
            print(f"  {hechos}/{len(faltan)}  {ritmo:.1f} frag/s  "
                  f"faltan ~{(len(faltan) - hechos) / ritmo / 60:.0f} min", flush=True)
    if particion:
        print(f"Trozo {particion[0]}/{particion[1]} listo: shards en {_dir_cache()}")
        return None
    matriz = np.stack([cache[k] for k in claves]).astype(np.float32)
    indice = faiss.IndexFlatIP(matriz.shape[1])
    indice.add(matriz)
    faiss.write_index(indice, str(config.FAISS_PATH))
    return {"modelo": config.ENCODER_MODEL, "revision": config.ENCODER_REVISION,
            "dimension": int(matriz.shape[1]), "max_seq_length": config.ENCODER_MAX_SEQ,
            "normalizado": True, "precision": "fp32", "faiss": "IndexFlatIP", "device": device}


# --- manifest ---------------------------------------------------------------------

def actualizar_manifest(chunks: list[dict]) -> None:
    ruta = config.MANIFEST_PATH
    try:
        manifest = json.loads(ruta.read_text(encoding="utf-8"))
        docs = manifest["documentos"]
    except (OSError, ValueError, KeyError) as e:
        print(f"AVISO: no se actualiza {ruta.name} ({e})")
        return
    resumen = {}
    if config.RESUMEN_INDICE_PATH.is_file():
        resumen = json.loads(config.RESUMEN_INDICE_PATH.read_text(encoding="utf-8"))["documentos"]
    por_doc: dict[str, int] = {}
    for c in chunks:
        por_doc[c["doc_id"]] = por_doc.get(c["doc_id"], 0) + 1
    cambios = 0
    for d in docs:
        n = por_doc.get(d["doc_id"], 0)
        sha = resumen.get(d["doc_id"], {}).get("sha256")
        if d.get("n_fragmentos") != n:
            d["n_fragmentos"] = n
            cambios += 1
        if sha and d.get("sha256") != sha:
            d["sha256"] = sha
            cambios += 1
    if "n_fragmentos" in manifest:
        manifest["n_fragmentos"] = sum(d.get("n_fragmentos", 0) for d in docs)
    ruta.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    en_manifest = {d["doc_id"] for d in docs}
    sin_manifest = sorted(set(por_doc) - en_manifest)
    sin_texto = sorted(d["doc_id"] for d in docs if d["doc_id"] not in por_doc)
    print(f"Manifest: {cambios} campos actualizados, n_fragmentos total {manifest.get('n_fragmentos')}")
    if sin_manifest:
        print(f"AVISO: {len(sin_manifest)} doc_id indexados que no estan en el manifest: {sin_manifest[:10]}")
    if sin_texto:
        print(f"AVISO: {len(sin_texto)} doc_id del manifest sin fragmentos (falta el .txt local?): {sin_texto[:10]}")


# --- main -------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--solo-bm25", action="store_true", help="no calcula embeddings ni index.faiss")
    ap.add_argument("--batch", type=int, default=16, help="batch del encoder (subir en GPU)")
    ap.add_argument("--particion", metavar="I/N", help="solo codifica el trozo I de N (1<=I<=N); sin index.faiss ni manifest")
    ap.add_argument("--no-manifest", action="store_true", help="no tocar corpus_manifest.json")
    args = ap.parse_args()

    particion = None
    if args.particion:
        try:
            i, n = (int(x) for x in args.particion.split("/"))
        except ValueError:
            ap.error("--particion debe ser I/N, p. ej. 2/3")
        if not 1 <= i <= n:
            ap.error("--particion: se exige 1 <= I <= N")
        if args.solo_bm25:
            ap.error("--particion no se combina con --solo-bm25")
        particion = (i, n)

    chunks = cargar_chunks()
    if particion:  # solo shards: no se toca bm25/, index.faiss, indice_info.json ni el manifest
        construir_denso(chunks, args.batch, particion)
        return 0
    config.INDICE_DIR.mkdir(parents=True, exist_ok=True)
    info = {
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_fragmentos": len(chunks),
        "sha256_chunks": sha256_bytes(config.CHUNKS_PATH.read_bytes()),
        "bm25": construir_bm25(chunks),
        "denso": None,
    }
    if config.RESUMEN_INDICE_PATH.is_file():
        info["version_segmentador"] = json.loads(
            config.RESUMEN_INDICE_PATH.read_text(encoding="utf-8")).get("version_segmentador")
    if args.solo_bm25:
        if config.FAISS_PATH.is_file():
            config.FAISS_PATH.unlink()  # un index.faiss de otra segmentacion quedaria desalineado
            print("Se borra index.faiss anterior (--solo-bm25: el denso no corresponde a estos fragmentos)")
    else:
        info["denso"] = construir_denso(chunks, args.batch)
    config.INDICE_INFO_PATH.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8", newline="\n")
    if not args.solo_bm25:
        n = config.verificar_indice()
        print(f"Indice verificado: {n} fragmentos")
    if not args.no_manifest:
        actualizar_manifest(chunks)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
