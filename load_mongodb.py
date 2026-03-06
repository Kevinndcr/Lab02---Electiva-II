"""
load_mongodb.py
===============
Carga del dataset eCommerce Purchase History en MongoDB.

Requisitos:
  - Contenedor MongoDB corriendo: docker compose up -d
  - Dataset en:                   data/kz.csv

Uso:
  python load_mongodb.py
"""

import time
import pymongo
import pandas as pd
from tqdm import tqdm

CSV_PATH   = "data/kz.csv"
CHUNK_SIZE = 10_000

def load_mongodb():
    print("[MongoDB] Conectando (localhost:27017)...")
    client = pymongo.MongoClient(
        "mongodb://admin:admin123@localhost:27017/",
        serverSelectionTimeoutMS=5000,
    )
    db  = client["ecommerce"]
    col = db["purchases"]

    # Índices para acelerar consultas posteriores
    col.create_index("category_code")
    col.create_index("brand")
    col.create_index("event_time")
    print("[MongoDB] Índices creados.")

    total = 0
    t0    = time.time()

    for chunk in tqdm(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE),
                      desc="[MongoDB]", unit="chunk"):
        chunk["event_time"] = pd.to_datetime(
            chunk["event_time"], utc=True, errors="coerce"
        )
        docs = chunk.where(pd.notnull(chunk), None).to_dict("records")
        col.insert_many(docs, ordered=False)
        total += len(docs)

    client.close()
    elapsed = time.time() - t0
    print(f"[MongoDB] ✓ {total:,} registros cargados en {elapsed:.1f}s ({total/elapsed:,.0f} reg/s)")


if __name__ == "__main__":
    load_mongodb()
