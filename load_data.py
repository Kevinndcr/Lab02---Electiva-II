"""
load_data.py
============
Carga optimizada del dataset eCommerce Purchase History (~2M registros)
en HBase, MongoDB y Redis.

Uso:
    python load_data.py                      # carga en los 3 motores
    python load_data.py mongodb              # solo MongoDB
    python load_data.py hbase redis          # HBase y Redis
"""

import sys
import time
import pandas as pd
from tqdm import tqdm

CSV_PATH   = "data/kz.csv"
CHUNK_SIZE = 10_000  # filas por lote


# ─────────────────────────────────────────────────────────────────────────────
# HBase  (happybase  →  Thrift server en localhost:9090)
# ─────────────────────────────────────────────────────────────────────────────
def load_hbase():
    import happybase

    print("\n[HBase] Conectando...")
    conn = happybase.Connection("localhost", port=9090)
    conn.open()

    table_name = b"ecommerce"
    families = {"event": dict(), "product": dict(), "user": dict()}

    if table_name not in conn.tables():
        print("[HBase] Creando tabla 'ecommerce'...")
        conn.create_table(table_name, families)

    table = conn.table(table_name)
    total = 0
    t0    = time.time()

    for chunk in tqdm(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE),
                      desc="[HBase]", unit="chunk"):
        with table.batch(batch_size=1000) as bat:
            for _, row in chunk.iterrows():
                row_key = f"{row.get('order_id', '')}_{row.get('product_id', '')}".encode()
                bat.put(row_key, {
                    b"event:time"    : str(row.get("event_time", "")).encode(),
                    b"product:id"    : str(row.get("product_id", "")).encode(),
                    b"product:cat"   : str(row.get("category_code", "")).encode(),
                    b"product:brand" : str(row.get("brand", "")).encode(),
                    b"product:price" : str(row.get("price", "")).encode(),
                    b"user:id"       : str(row.get("user_id", "")).encode(),
                })
        total += len(chunk)

    conn.close()
    elapsed = time.time() - t0
    print(f"[HBase] ✓ {total:,} registros cargados en {elapsed:.1f}s "
          f"({total/elapsed:,.0f} reg/s)")


# ─────────────────────────────────────────────────────────────────────────────
# MongoDB  (pymongo  →  localhost:27017)
# ─────────────────────────────────────────────────────────────────────────────
def load_mongodb():
    import pymongo

    print("\n[MongoDB] Conectando...")
    client = pymongo.MongoClient(
        "mongodb://admin:admin123@localhost:27017/",
        serverSelectionTimeoutMS=5000,
    )
    db  = client["ecommerce"]
    col = db["purchases"]

    # Índices antes de la carga para evitar re-indexado completo al final
    col.create_index("category_code")
    col.create_index("brand")
    col.create_index("event_time")

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
    print(f"[MongoDB] ✓ {total:,} registros cargados en {elapsed:.1f}s "
          f"({total/elapsed:,.0f} reg/s)")


# ─────────────────────────────────────────────────────────────────────────────
# Redis  (redis-py  →  localhost:6379)
# Estrategia:
#   HASH   order:<order_id>  →  campos del pedido
#   ZSET   sales:by_category →  score = cantidad de ventas
#   ZSET   revenue:by_brand  →  score = ingresos acumulados
#   ZSET   sales:by_month    →  score = cantidad de ventas
# ─────────────────────────────────────────────────────────────────────────────
def load_redis():
    import redis as redis_lib

    print("\n[Redis] Conectando...")
    r    = redis_lib.Redis(host="localhost", port=6379, decode_responses=True)
    pipe = r.pipeline(transaction=False)

    total = 0
    t0    = time.time()

    for chunk in tqdm(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE),
                      desc="[Redis]", unit="chunk"):
        chunk["event_time"] = pd.to_datetime(
            chunk["event_time"], utc=True, errors="coerce"
        )

        for _, row in chunk.iterrows():
            order_id = str(row.get("order_id", ""))
            category = str(row.get("category_code", "unknown") or "unknown")
            brand    = str(row.get("brand", "unknown") or "unknown")
            try:
                price = float(row.get("price", 0) or 0)
                if price != price:  # NaN check
                    price = 0.0
            except (ValueError, TypeError):
                price = 0.0
            ts       = row["event_time"]
            month    = ts.strftime("%Y-%m") if pd.notnull(ts) else "unknown"

            pipe.hset(f"order:{order_id}", mapping={
                "product_id"    : str(row.get("product_id", "")),
                "category_code" : category,
                "brand"         : brand,
                "price"         : str(price),
                "user_id"       : str(row.get("user_id", "")),
                "event_time"    : str(row.get("event_time", "")),
            })
            pipe.zincrby("sales:by_category", 1,      category)
            pipe.zincrby("revenue:by_brand",  price,   brand)
            pipe.zincrby("sales:by_month",    1,       month)

        pipe.execute()
        total += len(chunk)

    elapsed = time.time() - t0
    print(f"[Redis] ✓ {total:,} registros cargados en {elapsed:.1f}s "
          f"({total/elapsed:,.0f} reg/s)")


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    targets = [t.lower() for t in sys.argv[1:]] or ["hbase", "mongodb", "redis"]

    print(f"Motores a cargar: {targets}")
    print(f"Dataset         : {CSV_PATH}")
    print(f"Tamaño de chunk : {CHUNK_SIZE:,} filas\n")

    if "hbase"   in targets:
        load_hbase()
    if "mongodb" in targets:
        load_mongodb()
    if "redis"   in targets:
        load_redis()

    print("\n✓ Carga finalizada.")
