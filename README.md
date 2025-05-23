# system-health-monitor-etl
Python-based System Health Monitor, is focused on building a modular ETL-style data pipeline that fetches system metrics (like CPU, memory, or other API-based stats), processes them, and stores them in a structured format or database.

# 🖥️ System Health Monitor ETL

A modern, real-time system health monitoring backend built with Python’s asynchronous stack — combining FastAPI, WebSockets, PostgreSQL, Redis, and Docker.

## 📌 Project Goals

This ETL system collects, transforms, stores, and streams real-time system metrics (CPU, memory, disk, network) using an efficient asynchronous architecture.

---

## 🚀 Features

- 📡 **Real-time Monitoring** via FastAPI WebSockets
- 🔄 **ETL Pipeline** with AsyncIO and `psutil`
- 🧰 **Live Streaming** with Redis Pub/Sub
- 🗃️ **Data Storage** in PostgreSQL via async SQLAlchemy
- 🔌 **REST API** to access snapshots & logs
- 🐳 **Dockerized** for local & production deployments
- ✅ **Testable** with Pytest + HTTPX

---

## 🧱 Tech Stack

| Layer         | Tool                              |
| ------------- | --------------------------------- |
| Language      | Python 3.11+                      |
| API Framework | FastAPI                           |
| ETL Pipeline  | AsyncIO, psutil                   |
| Realtime Comm | FastAPI WebSockets, Redis pub/sub |
| Storage       | PostgreSQL + SQLAlchemy (async)   |
| Message Bus   | Redis (via Docker)                |
| DevOps        | Docker + Docker Compose           |
| Testing       | Pytest + HTTPX (async)            |
| Monitoring    | Logging + Metrics API             |

---

## 📂 Folder Structure

system_health_monitor_etl/
├── app/
│ ├── api/ # FastAPI routes + WebSocket
│ ├── ingestion/ # Collect system metrics (via psutil)
│ ├── transformation/ # Clean/normalize health data
│ ├── storage/ # Store to Postgres or push to Redis
│ ├── models/ # Pydantic + SQLAlchemy schemas
│ ├── utils/ # Logging, Redis, etc.
│ ├── main.py # App startup
│ ├── config.py # Settings via Pydantic
├── tests/ # Unit + integration tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md