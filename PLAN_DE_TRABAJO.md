# Plan de Trabajo – Laboratorio #02
**Bases de Datos No Relacionales con Docker: HBase, MongoDB y Redis**

---

## Integrantes
| Integrante | Sistema Operativo a cubrir |
|---|---|
| Integrante 1 | Windows |
| Integrante 2 | Linux (modo consola) |

---

## Fases y Tareas

### FASE 1 – Investigación y configuración del entorno (Día 1–2)
- [ ] Investigar arquitectura y características de HBase, MongoDB y Redis
- [ ] Instalar Docker Desktop (Windows) / Docker Engine (Linux)
- [ ] Instalar Python 3.10+ y pip
- [ ] Instalar Jupyter Notebook / JupyterLab
- [ ] Instalar librerías Python: `happybase`, `pymongo`, `redis`
- [ ] Crear el archivo `docker-compose.yml` con los 3 servicios
- [ ] Verificar que los 3 contenedores levanten correctamente

### FASE 2 – Carga de datos (Día 2–3)
- [ ] Descargar el dataset *eCommerce Purchase History from Electronics Store* (Kaggle)
- [ ] Analizar la estructura y columnas del dataset
- [ ] Diseñar el esquema de datos para cada motor:
  - HBase: familias de columnas
  - MongoDB: estructura del documento
  - Redis: estructura de hash/sorted set
- [ ] Crear `load_data.py`: script optimizado de carga con batch/pipeline
- [ ] Ejecutar y verificar la carga en los 3 motores
- [ ] Medir y registrar tiempos de carga

### FASE 3 – Consultas nativas (Día 3–4)
- [ ] HBase: usar HBase Shell y/o Apache Phoenix
- [ ] MongoDB: usar MongoDB Compass o mongosh
- [ ] Redis: usar redis-cli
- [ ] Documentar herramienta, sintaxis de consulta y visualización de resultados para:
  - Categoría más vendida
  - Marca con mayores ingresos brutos
  - Mes con más ventas (UTC)

### FASE 4 – Scripts Python de consultas (Día 4–5)
- [ ] Crear `queries_hbase.ipynb`
- [ ] Crear `queries_mongodb.ipynb`
- [ ] Crear `queries_redis.ipynb`
- [ ] Cada notebook debe incluir:
  - Las 3 consultas solicitadas
  - Tablas de salida (`pandas` / `tabulate`)
  - Al menos un gráfico por consulta (`matplotlib` / `seaborn`)
  - Medición de tiempos de respuesta (`time` / `timeit`)

### FASE 5 – Documentación y entrega (Día 5–6)
- [ ] Redactar documento `.pdf` con:
  - Portada
  - Descripción teórica de cada motor (HBase, MongoDB, Redis)
  - Pasos de creación y gestión de cada base de datos
  - Resultados obtenidos con capturas
  - Análisis comparativo de tiempos
  - Conclusiones
  - Bibliografía
- [ ] Organizar estructura del proyecto (ver abajo)
- [ ] Comprimir en `.zip` y subir a la plataforma

---

## Estructura de Entrega Esperada

```
LabII/
├── docker-compose.yml
├── load_data.py
├── queries/
│   ├── queries_hbase.ipynb
│   ├── queries_mongodb.ipynb
│   └── queries_redis.ipynb
├── data/
│   └── (dataset .csv – no subir a GitHub si supera el límite)
├── docs/
│   └── Laboratorio02_Documentacion.pdf
└── README.md
```

---

## Herramientas y Tecnologías

| Categoría | Tecnología |
|---|---|
| Contenedores | Docker / Docker Compose |
| Bases de datos | HBase, MongoDB, Redis |
| Lenguaje | Python 3.10+ |
| Librerías Python | happybase, pymongo, redis, pandas, matplotlib, seaborn, tqdm |
| Consultas nativas | HBase Shell / Phoenix, mongosh / Compass, redis-cli |
| Notebooks | Jupyter Notebook / JupyterLab |
| Documentación | Word → PDF |

---

## Criterios de Éxito
- Los 3 contenedores levantan sin errores con un solo `docker compose up`
- El script de carga inserta los ~2 millones de registros de forma optimizada
- Las consultas devuelven resultados correctos y tiempos medidos
- El ZIP contiene todos los archivos en la estructura correcta
- El PDF tiene portada, desarrollo con capturas, conclusiones y bibliografía
