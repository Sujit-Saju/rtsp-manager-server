# RTSP Manager Server

A high-performance, asynchronous REST API service built with **Quart** and **SQLAlchemy** (using **aiosqlite**) for managing RTSP video streams, camera configurations, and sequence generation. 

## Features

- **Asynchronous Architecture**: Fully async backend powered by **Quart** (Flask-compatible ASGI framework) and **Hypercorn**.
- **Database Engine**: Async database access using **SQLAlchemy 2.0** and **aiosqlite** (SQLite).
- **Auto-Migrating Schema**: Automated database table creation on startup.
- **RESTful Stream Management**: Endpoints for creating, updating, retrieving, and deleting video streams.
- **Unique Code Generator**: Dedicated service for managing and generating custom unique codes (e.g. `STREAM00001`) with configurable prefixes, width, and date structures.
- **Interactive API Docs**: Automatic Swagger UI/OpenAPI documentation generation via `quart-schema`.
- **CORS-enabled**: Multi-origin configurations out of the box.

---

## Tech Stack

- **Framework**: [Quart](https://pgjones.gitlab.io/quart/)
- **ASGI Server**: [Hypercorn](https://pgjones.gitlab.io/hypercorn/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database Driver**: [aiosqlite](https://github.com/omnilib/aiosqlite)
- **API Spec**: [Quart-Schema](https://github.com/pgjones/quart-schema)

---

## Directory Structure

```text
rtsp-manager-server/
├── app/
│   ├── controller/          # Route handlers & blueprint registration
│   ├── core/                # Configuration, logging, and common utilities
│   ├── database/            # DB engine initialization & declarative base
│   ├── models/              # SQLAlchemy database models
│   ├── repositories/        # Data access layer (generic CRUD operations)
│   ├── schemas/             # Request/response validation schemas
│   ├── services/            # Business logic layer
│   └── utils/               # Common helper functions
├── logs/                    # Application runtime logs
├── uploads/                 # Directory for media uploads / stream recordings
├── .env.example             # Example environment configuration
├── run.py                   # Application entry point
└── requirements.txt         # Package dependencies
```

---

## Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Setup Virtual Environment
Clone the repository, navigate to the project directory, and create a virtual environment:

```bash
# Create venv
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate venv (Windows CMD)
.\venv\Scripts\activate.bat

# Activate venv (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Install all required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and adjust variables as needed:

```bash
cp .env.example .env
```

Default settings in `.env`:
- `HOST`: Bind address (default: `0.0.0.0`)
- `PORT`: Port to listen on (default: `5000`)
- `DATABASE_URL`: Connection string (default: `sqlite+aiosqlite:///rtsp_manager.db`)
- `RTSP_PORT`: Default RTSP port (default: `8554`)

---

## Running the Application

Start the development server:

```bash
python run.py
```

Upon starting:
1. The app automatically runs database schema migration to check and generate required tables (`streams` and `tbl_seq_number`).
2. The server spins up at: `http://localhost:5000` (or whichever port is configured in your `.env` file).

---

## API Documentation

Interactive OpenAPI documentation is available via Swagger UI. Once the server is running, navigate to:

- **Swagger UI**: [http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs)
- **OpenAPI Schema**: [http://localhost:5000/api/v1/openapi.json](http://localhost:5000/api/v1/openapi.json)

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/api/v1/streams` | Register/Create a new stream |
| **GET** | `/api/v1/streams` | Retrieve all registered streams |
| **GET** | `/api/v1/streams/<uniq_code>` | Retrieve details of a specific stream |
| **PUT** | `/api/v1/streams/<uniq_code>` | Update an existing stream |
| **DELETE** | `/api/v1/streams/<uniq_code>` | Delete a stream registration |

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
