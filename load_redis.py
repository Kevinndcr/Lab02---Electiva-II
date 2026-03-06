"""
load_redis.py
=============
Carga del dataset eCommerce Purchase History en Redis.

Estrategia de almacenamiento:
  HASH  order:<order_id>      → campos de cada pedido
  ZSET  sales:by_category     → score = cantidad de ventas por categoría
  ZSET  revenue:by_brand      → score = ingresos acumulados por marca
  ZSET  sales:by_month        → score = cantidad de ventas por mes (UTC)

Requisitos:
  - Contenedor Redis corriendo: docker compose up -d
  - Dataset en:                 data/kz.csv

Uso:
  python load_redis.py
"""

import time
import redis
import pandas as pd
from tqdm import tqdm

CSV_PATH   = "data/kz.csv"
CHUNK_SIZE = 10_000

def load_redis():
    print("[Redis] Conectando (localhost:6379)...")
    r    = redis.Redis(host="localhost", port=6379, decode_responses=True)
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
            ts    = row["event_time"]
            month = ts.strftime("%Y-%m") if pd.notnull(ts) else "unknown"

            pipe.hset(f"order:{order_id}", mapping={
                "product_id"    : str(row.get("product_id", "")),
                "category_code" : category,
                "brand"         : brand,
                "price"         : str(price),
                "user_id"       : str(row.get("user_id", "")),
                "event_time"    : str(row.get("event_time", "")),
            })
            pipe.zincrby("sales:by_category", 1,     category)
            pipe.zincrby("revenue:by_brand",  price,  brand)
            pipe.zincrby("sales:by_month",    1,      month)

        pipe.execute()
        total += len(chunk)

    elapsed = time.time() - t0
    print(f"[Redis] ✓ {total:,} registros cargados en {elapsed:.1f}s ({total/elapsed:,.0f} reg/s)")


if __name__ == "__main__":
    load_redis()
