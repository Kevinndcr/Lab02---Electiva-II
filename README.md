# Laboratorio #02 – Motores NoSQL con Docker

Instalación y uso de **HBase**, **MongoDB** y **Redis** mediante Docker Compose,
con carga de 2 millones de registros del dataset *eCommerce Purchase History from
Electronics Store* y consultas desde Python.

---

## Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows con WSL2) o Docker Engine (Linux)
- Python 3.10+

---

## Inicio rápido

```bash
# 1. Levantar los 3 contenedores
docker compose up -d

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate        # Linux
.\venv\Scripts\Activate.ps1     # Windows

pip install -r requirements.txt

# 3. Descargar el dataset (requiere cuenta Kaggle)
kaggle datasets download mkechinov/ecommerce-purchase-history-from-electronics-store -p data/ --unzip

# 4. Cargar datos en los 3 motores
python load_data.py

# 5. Abrir notebooks de consultas
jupyter lab
```

---

## Estructura del proyecto

```
LabII/
├── docker-compose.yml          ← HBase + MongoDB + Redis
├── load_data.py                ← Script de carga optimizado
├── requirements.txt
├── README.md
├── PLAN_DE_TRABAJO.md          ← Fases, tareas y criterios de éxito
├── GUIA_PASO_A_PASO.md         ← Instalaciones y ejecuciones detalladas
├── data/                       ← Dataset CSV (no incluido en repo)
├── queries/
│   ├── queries_hbase.ipynb
│   ├── queries_mongodb.ipynb
│   └── queries_redis.ipynb
└── docs/
    └── Laboratorio02_Documentacion.pdf
```

---

## Puertos y credenciales

| Servicio | Puerto | Credencial |
|---|---|---|
| HBase Thrift | 9090 | – |
| HBase Web UI | 16010 | – |
| MongoDB | 27017 | admin / admin123 |
| Redis | 6379 | – |

---

## Consultas implementadas

1. ¿Cuál es la categoría más vendida?
2. ¿Qué marca (brand) generó más ingresos brutos?
3. ¿Qué mes tuvo más ventas? (UTC)

Resultados con tablas y gráficos en los notebooks de la carpeta `queries/`.
