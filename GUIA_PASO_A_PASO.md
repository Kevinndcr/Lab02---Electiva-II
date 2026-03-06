# Guía Paso a Paso – Laboratorio #02
**HBase + MongoDB + Redis con Docker y Python**

---

## Índice
1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación de Docker](#2-instalación-de-docker)
3. [Configuración de Docker Compose](#3-configuración-de-docker-compose)
4. [Levantar los contenedores](#4-levantar-los-contenedores)
5. [Configuración del entorno Python](#5-configuración-del-entorno-python)
6. [Descarga del dataset](#6-descarga-del-dataset)
7. [Carga de datos en los 3 motores](#7-carga-de-datos-en-los-3-motores)
8. [Consultas nativas](#8-consultas-nativas)
9. [Scripts Python de consultas (Jupyter)](#9-scripts-python-de-consultas-jupyter)
10. [Estructura final y empaquetado](#10-estructura-final-y-empaquetado)

---

## 1. Requisitos previos

### Windows
- Windows 10/11 (64-bit) con WSL2 habilitado
- Python 3.10 o superior
- Git

### Linux (consola, sin GUI)
- Ubuntu 22.04 LTS o similar
- Python 3.10 o superior
- curl, wget

---

## 2. Instalación de Docker

### 2.1 – Windows: habilitar WSL2 (si no está activo)

```powershell
# Ejecutar en PowerShell como Administrador
wsl --install
wsl --set-default-version 2
```

Reiniciar el equipo y luego instalar **Docker Desktop** desde:  
https://www.docker.com/products/docker-desktop/

Verificar instalación:
```powershell
docker --version
docker compose version
```

### 2.2 – Linux (Ubuntu/Debian)

```bash
# Desinstalar versiones antiguas
sudo apt remove docker docker-engine docker.io containerd runc -y

# Instalar dependencias
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Agregar repositorio oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine y Compose plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker (evita usar sudo siempre)
sudo usermod -aG docker $USER
newgrp docker

# Verificar
docker --version
docker compose version
```

---

## 3. Configuración de Docker Compose

Crear el archivo `docker-compose.yml` en la raíz del proyecto con el siguiente contenido:

```yaml
version: "3.8"

services:

  # ─── HBase (standalone con Thrift server para acceso desde Python) ───────
  hbase:
    image: dajobe/hbase
    container_name: hbase
    ports:
      - "16000:16000"   # HBase Master
      - "16010:16010"   # HBase Master Web UI
      - "16020:16020"   # HBase RegionServer
      - "16030:16030"   # RegionServer Web UI
      - "9090:9090"     # Thrift API (usado por happybase)
      - "9095:9095"     # Thrift Web UI
      - "2181:2181"     # ZooKeeper
    environment:
      - HBASE_MANAGES_ZK=true
    networks:
      - labnet

  # ─── MongoDB ──────────────────────────────────────────────────────────────
  mongodb:
    image: mongo:7.0
    container_name: mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
      MONGO_INITDB_DATABASE: ecommerce
    volumes:
      - mongo_data:/data/db
    networks:
      - labnet

  # ─── Redis ────────────────────────────────────────────────────────────────
  redis:
    image: redis:7.2-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - labnet

volumes:
  mongo_data:
  redis_data:

networks:
  labnet:
    driver: bridge
```

---

## 4. Levantar los contenedores

Desde la carpeta raíz del proyecto (donde está el `docker-compose.yml`):

```bash
# Levantar todos los servicios en segundo plano
docker compose up -d

# Verificar estado de los contenedores
docker compose ps

# Ver logs de un servicio específico (ej: hbase)
docker compose logs hbase

# Detener todos los servicios (sin borrar datos)
docker compose stop

# Detener y borrar contenedores (los volúmenes persisten)
docker compose down

# Detener, borrar contenedores Y volúmenes (reset total)
docker compose down -v
```

### Verificar conectividad

**HBase** – Iniciar el servidor Thrift (requerido para conectarse desde Python):
```bash
# Iniciar Thrift en segundo plano (ejecutar una vez después de levantar el contenedor)
docker exec -d hbase hbase thrift start
# Esperar ~15 segundos antes de usar Python
```

Acceder al shell desde dentro del contenedor:
```bash
docker exec -it hbase hbase shell
# Dentro del shell:
status
list
exit
```

**MongoDB** – Conectarse con mongosh:
```bash
docker exec -it mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
# Dentro de mongosh:
show dbs
use ecommerce
exit
```

**Redis** – Conectarse con redis-cli:
```bash
docker exec -it redis redis-cli
# Dentro de redis-cli:
PING        # debe responder PONG
INFO server
exit
```

---

## 5. Configuración del entorno Python

### 5.1 – Crear entorno virtual

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux
python3 -m venv venv
source venv/bin/activate
```

### 5.2 – Instalar librerías

```bash
pip install --upgrade pip

# Bases de datos
pip install happybase         # HBase via Thrift
pip install pymongo           # MongoDB
pip install redis             # Redis

# Datos y análisis
pip install pandas numpy tqdm

# Visualización
pip install matplotlib seaborn

# Jupyter
pip install jupyterlab notebook

# Utilidades
pip install python-dotenv kaggle
```

Generar `requirements.txt`:
```bash
pip freeze > requirements.txt
```
Igual, por supuesto se puede hacer simplemente haciendo pip install -r requirements.txt :P

### 5.3 – Lanzar JupyterLab

```bash
jupyter lab
# Abrir en el navegador: http://localhost:8888
```

---

## 6. Descarga del dataset

### Opción A – Descarga manual
1. Ir a: https://www.kaggle.com/datasets/mkechinov/ecommerce-purchase-history-from-electronics-store
2. Iniciar sesión en Kaggle
3. Descargar el archivo `.csv` (~300 MB comprimido)
4. Colocar el CSV en la carpeta `data/` del proyecto

### Opción B – Kaggle API (recomendada)

```bash
# Instalar kaggle CLI
pip install kaggle

# Configurar credenciales:
# 1. Ir a https://www.kaggle.com/account → "Create New API Token"
# 2. Descargar kaggle.json
# 3. Colocar en:
#    Windows: C:\Users\<usuario>\.kaggle\kaggle.json
#    Linux:   ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json   # solo Linux

# Descargar dataset
mkdir -p data
kaggle datasets download \
  mkechinov/ecommerce-purchase-history-from-electronics-store \
  -p data/ --unzip
```

### Inspección rápida del dataset

```python
import pandas as pd

df = pd.read_csv("data/kz.csv", nrows=5)
print(df.columns.tolist())
print(df.dtypes)
print(df.head())
```

Columnas esperadas:
```
event_time, order_id, product_id, category_id, category_code,
brand, price, user_id
```

---

## 7. Carga de datos en los 3 motores (Después de descargar el csv con la opción A o B)

Crear `load_data.py` con el siguiente contenido:
(Si se descarga desde el git, ya estos archivos están incluidos xd)

```python
"""
load_data.py  –  Carga del dataset eCommerce en HBase, MongoDB y Redis
Requiere que los contenedores Docker estén corriendo (docker compose up -d)
"""

import pandas as pd
import happybase
import pymongo
import redis
import time
from tqdm import tqdm

CSV_PATH    = "data/kz.csv"
CHUNK_SIZE  = 10_000   # registros procesados por lote

# ─────────────────────────────────────────────────────────
# 1. HBase
# ─────────────────────────────────────────────────────────
def load_hbase(df_iter):
    """Carga en HBase usando put por lotes (batch)."""
    conn = happybase.Connection("localhost", port=9090)
    conn.open()

    table_name = b"ecommerce"
    families   = {b"event": dict(), b"product": dict(), b"user": dict()}

    if table_name not in conn.tables():
        conn.create_table(table_name, families)

    table = conn.table(table_name)
    total = 0
    t0    = time.time()

    for chunk in df_iter:
        with table.batch(batch_size=1000) as bat:
            for _, row in chunk.iterrows():
                row_key = f"{row['order_id']}_{row['product_id']}".encode()
                bat.put(row_key, {
                    b"event:time"     : str(row.get("event_time", "")).encode(),
                    b"product:id"     : str(row.get("product_id", "")).encode(),
                    b"product:cat"    : str(row.get("category_code", "")).encode(),
                    b"product:brand"  : str(row.get("brand", "")).encode(),
                    b"product:price"  : str(row.get("price", "")).encode(),
                    b"user:id"        : str(row.get("user_id", "")).encode(),
                })
        total += len(chunk)
        print(f"[HBase] {total:,} registros cargados...")

    conn.close()
    print(f"[HBase] Carga completa: {total:,} registros en {time.time()-t0:.1f}s")


# ─────────────────────────────────────────────────────────
# 2. MongoDB
# ─────────────────────────────────────────────────────────
def load_mongodb(df_iter):
    """Carga en MongoDB usando insert_many con ordered=False."""
    client = pymongo.MongoClient(
        "mongodb://admin:admin123@localhost:27017/",
        serverSelectionTimeoutMS=5000
    )
    db         = client["ecommerce"]
    collection = db["purchases"]

    # Índices para acelerar consultas posteriores
    collection.create_index("category_code")
    collection.create_index("brand")
    collection.create_index("event_time")

    total = 0
    t0    = time.time()

    for chunk in df_iter:
        chunk["event_time"] = pd.to_datetime(chunk["event_time"], utc=True, errors="coerce")
        docs = chunk.where(pd.notnull(chunk), None).to_dict("records")
        collection.insert_many(docs, ordered=False)
        total += len(docs)
        print(f"[MongoDB] {total:,} registros cargados...")

    client.close()
    print(f"[MongoDB] Carga completa: {total:,} registros en {time.time()-t0:.1f}s")


# ─────────────────────────────────────────────────────────
# 3. Redis
# ─────────────────────────────────────────────────────────
def load_redis(df_iter):
    """
    Estrategia Redis:
      - Hash por orden:   HSET order:<order_id> field value ...
      - Contador de ventas por categoría: ZINCRBY sales:by_category <score> <member>
      - Contador de ingresos por marca:   ZINCRBY revenue:by_brand <score> <member>
      - Contador de ventas por mes:       ZINCRBY sales:by_month <score> <member>
    """
    r     = redis.Redis(host="localhost", port=6379, decode_responses=True)
    pipe  = r.pipeline(transaction=False)
    total = 0
    t0    = time.time()

    for chunk in df_iter:
        chunk["event_time"] = pd.to_datetime(chunk["event_time"], utc=True, errors="coerce")

        for _, row in chunk.iterrows():
            order_id = str(row.get("order_id", ""))
            category = str(row.get("category_code", "unknown"))
            brand    = str(row.get("brand", "unknown"))
            price    = float(row.get("price", 0) or 0)
            month    = row["event_time"].strftime("%Y-%m") if pd.notnull(row["event_time"]) else "unknown"

            pipe.hset(f"order:{order_id}", mapping={
                "product_id"    : str(row.get("product_id", "")),
                "category_code" : category,
                "brand"         : brand,
                "price"         : price,
                "user_id"       : str(row.get("user_id", "")),
                "event_time"    : str(row.get("event_time", "")),
            })
            pipe.zincrby("sales:by_category", 1,     category)
            pipe.zincrby("revenue:by_brand",  price,  brand)
            pipe.zincrby("sales:by_month",    1,     month)

        pipe.execute()
        total += len(chunk)
        print(f"[Redis] {total:,} registros cargados...")

    print(f"[Redis] Carga completa: {total:,} registros en {time.time()-t0:.1f}s")


# ─────────────────────────────────────────────────────────
# Ejecución principal
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] or ["hbase", "mongodb", "redis"]

    reader = lambda: pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE)

    if "hbase"   in targets: load_hbase(reader())
    if "mongodb" in targets: load_mongodb(reader())
    if "redis"   in targets: load_redis(reader())
```

### Ejecutar la carga (Desde el venv que se creó anteriormente)

```bash
# Cargar en los 3 motores 

# Importante, este script los carga todos a la vez, pero también se pueden ejecutar en los distintos .py (hbase, mongo, redis .py para la carga de cada bd de manera individual)
python load_data.py

# Cargar solo en uno
python load_data.py mongodb
python load_data.py redis
python load_data.py hbase
```

---

## 8. Consultas nativas

### 8.1 – HBase Shell

```bash
docker exec -it hbase hbase shell
```

```ruby
# Listar tablas
list

# Ver esquema de la tabla
describe 'ecommerce'

# Contar filas (puede tardar)
count 'ecommerce'

# Obtener una fila
get 'ecommerce', '<row_key>'

# Escanear primeros 10 registros
scan 'ecommerce', {LIMIT => 10}

# Filtrar por columna (brand = 'samsung')
scan 'ecommerce', {
  FILTER => "SingleColumnValueFilter('product','brand',=,'binary:samsung')",
  LIMIT => 20
}
```

### 8.2 – MongoDB (mongosh)

```bash
docker exec -it mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
```

```javascript
use ecommerce

// Categoría más vendida (excluye NaN y null)
db.purchases.aggregate([
  { $match: { category_code: { $type: "string" } } },
  { $group: { _id: "$category_code", total: { $sum: 1 } } },
  { $sort: { total: -1 } },
  { $limit: 1 }
])

// Marca con más ingresos brutos (excluye NaN y null)
db.purchases.aggregate([
  { $match: { brand: { $type: "string" } } },
  { $group: { _id: "$brand", revenue: { $sum: "$price" } } },
  { $sort: { revenue: -1 } },
  { $limit: 1 }
])

// Mes con más ventas
db.purchases.aggregate([
  { $project: { month: { $dateToString: { format: "%Y-%m", date: "$event_time" } } } },
  { $group: { _id: "$month", total: { $sum: 1 } } },
  { $sort: { total: -1 } },
  { $limit: 1 }
])
```

### 8.3 – Redis CLI

```bash
docker exec -it redis redis-cli
```

```bash
# Categoría más vendida (el miembro con mayor score)
ZREVRANGE sales:by_category 0 0 WITHSCORES

# Top 5 categorías
ZREVRANGE sales:by_category 0 4 WITHSCORES

# Marca con más ingresos
ZREVRANGE revenue:by_brand 0 0 WITHSCORES

# Mes con más ventas
ZREVRANGE sales:by_month 0 0 WITHSCORES

# Ver un hash de orden específico
HGETALL order:<order_id>

# Total de claves cargadas
DBSIZE
```

---

## 9. Scripts Python de consultas (Jupyter)

### Lanzar JupyterLab

```bash
# Activar entorno virtual primero
# Windows:
.\venv\Scripts\Activate.ps1
# Linux:
source venv/bin/activate

# Lanzar Jupyter
jupyter lab
```

Crear los siguientes notebooks en la carpeta `queries/`:

---

### `queries_mongodb.ipynb` – Estructura base

```python
# Celda 1 – Conexión
import pymongo, pandas as pd, time
import matplotlib.pyplot as plt, seaborn as sns

client = pymongo.MongoClient("mongodb://admin:admin123@localhost:27017/")
db     = client["ecommerce"]
col    = db["purchases"]

# Celda 2 – Q1: Categoría más vendida
t0 = time.time()
pipeline = [
    {"$group": {"_id": "$category_code", "total": {"$sum": 1}}},
    {"$sort":  {"total": -1}},
    {"$limit": 10}
]
result = list(col.aggregate(pipeline))
print(f"Tiempo: {time.time()-t0:.3f}s")
df_q1 = pd.DataFrame(result).rename(columns={"_id": "category", "total": "count"})
display(df_q1)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_q1, x="category", y="count", ax=ax, palette="viridis")
ax.set_title("Top 10 Categorías más vendidas (MongoDB)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
plt.tight_layout(); plt.show()
```

### `queries_redis.ipynb` – Estructura base

```python
# Celda 1 – Conexión
import redis, pandas as pd, time
import matplotlib.pyplot as plt, seaborn as sns

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Celda 2 – Q1: Categoría más vendida
t0     = time.time()
result = r.zrevrange("sales:by_category", 0, 9, withscores=True)
print(f"Tiempo: {time.time()-t0:.6f}s")
df_q1  = pd.DataFrame(result, columns=["category", "count"])
display(df_q1)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_q1, x="category", y="count", ax=ax, palette="magma")
ax.set_title("Top 10 Categorías más vendidas (Redis)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
plt.tight_layout(); plt.show()
```

### `queries_hbase.ipynb` – Estructura base

```python
# Celda 1 – Conexión
import happybase, pandas as pd, time
from collections import Counter
import matplotlib.pyplot as plt, seaborn as sns

conn  = happybase.Connection("localhost", port=9090)
conn.open()
table = conn.table("ecommerce")

# Celda 2 – Q1: Categoría más vendida (scan + conteo en Python)
t0      = time.time()
counter = Counter()
for key, data in table.scan(columns=[b"product:cat"]):
    cat = data.get(b"product:cat", b"unknown").decode()
    counter[cat] += 1
print(f"Tiempo: {time.time()-t0:.3f}s")
df_q1 = pd.DataFrame(counter.most_common(10), columns=["category", "count"])
display(df_q1)

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_q1, x="category", y="count", ax=ax, palette="plasma")
ax.set_title("Top 10 Categorías más vendidas (HBase)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
plt.tight_layout(); plt.show()
```

---

## 10. Estructura final y empaquetado

### Estructura del proyecto

```
LabII/
├── docker-compose.yml
├── load_data.py
├── requirements.txt
├── README.md
├── data/
│   └── kz.csv               ← dataset (no subir a GitHub)
├── queries/
│   ├── queries_hbase.ipynb
│   ├── queries_mongodb.ipynb
│   └── queries_redis.ipynb
└── docs/
    └── Laboratorio02_Documentacion.pdf
```

### Crear el .zip para entrega

```bash
# Windows (PowerShell)
Compress-Archive -Path LabII\ -DestinationPath Entrega_LabII.zip

# Linux
zip -r Entrega_LabII.zip LabII/ --exclude "LabII/data/*" --exclude "LabII/venv/*"
```

### README.md recomendado

```markdown
# Laboratorio #02 – NoSQL con Docker

## Requisitos
- Docker + Docker Compose
- Python 3.10+

## Levantar entorno
    docker compose up -d

## Instalar dependencias Python
    pip install -r requirements.txt

## Cargar datos
    python load_data.py

## Ejecutar consultas
    jupyter lab
    # Abrir carpeta queries/
```

---

## Resumen de puertos y credenciales

| Servicio | Puerto | Credencial |
|---|---|---|
| HBase Thrift | 9090 | (sin auth) |
| HBase Web UI | 16010 | (sin auth) |
| MongoDB | 27017 | admin / admin123 |
| Redis | 6379 | (sin auth) |
| JupyterLab | 8888 | (token en terminal) |
