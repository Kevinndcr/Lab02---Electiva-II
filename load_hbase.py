"""
load_hbase.py
=============
Carga del dataset eCommerce Purchase History en HBase.

Requisitos:
  - Contenedor HBase corriendo: docker compose up -d
  - Thrift iniciado:            docker exec -d hbase hbase thrift start
  - Dataset en:                 data/kz.csv

Uso:
  python load_hbase.py
"""

import time
import happybase
import pandas as pd
from tqdm import tqdm

CSV_PATH   = "data/kz.csv"
CHUNK_SIZE = 10_000

def load_hbase():
    print("[HBase] Conectando al servidor Thrift (localhost:9090)...")
    conn = happybase.Connection("localhost", port=9090)
    conn.open()

    table_name = b"ecommerce"
    families   = {"event": dict(), "product": dict(), "user": dict()}

    if table_name not in conn.tables():
        print("[HBase] Creando tabla 'ecommerce'...")
        conn.create_table(table_name, families)
    else:
        print("[HBase] Tabla 'ecommerce' ya existe, continuando...")

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
    print(f"[HBase] ✓ {total:,} registros cargados en {elapsed:.1f}s ({total/elapsed:,.0f} reg/s)")


if __name__ == "__main__":
    load_hbase()
