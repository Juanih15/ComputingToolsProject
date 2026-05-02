# Flask-Mongo CI/CD Pipeline

A task management API built with **Flask** and **MongoDB**, containerized with **Docker**, and automated with **Jenkins**.

## Architecture

```
GitHub  →  Jenkins  →  Docker Compose  →  Flask + MongoDB
                          │
                          ├── flask_app  (Python 3.12, port 5000)
                          └── mongo     (MongoDB 7, port 27017)
```

**Tools used:**
| Tool | Purpose |
|------|---------|
| GitHub | Version control and collaboration |
| Jenkins | CI/CD pipeline automation |
| Docker | Containerization of the Flask app |
| Docker Compose | Multi-container orchestration (Flask + MongoDB) |
| MongoDB | NoSQL database for task storage |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | App info and endpoint listing |
| GET | `/health` | Health check (verifies MongoDB connection) |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task (`{"title": "...", "description": "..."}`) |
| GET | `/tasks/<id>` | Get a single task by ID |
| DELETE | `/tasks/<id>` | Delete a task by ID |

## Setup & Run

### Prerequisites
- Docker and Docker Compose installed
- Jenkins (for CI/CD pipeline)

### Run Locally
```bash
cd flask-mongo-pipeline
docker compose up --build -d
```
The app will be available at **http://localhost:5000**.

### Test It
```bash
# Health check
curl http://localhost:5000/health

# Create a task
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Hello world"}'

# List tasks
curl http://localhost:5000/tasks
```

### Tear Down
```bash
cd flask-mongo-pipeline
docker compose down -v
```

## Jenkins Pipeline

The `Jenkinsfile` defines a 5-stage pipeline:

1. **Checkout** — Pulls the latest code from GitHub
2. **Build** — Builds Docker images via `docker compose build`
3. **Verify** — Confirms the images exist
4. **Deploy** — Starts the containers with `docker compose up -d`
5. **Test** — Runs smoke tests against the live endpoints:
   - Verifies `/health` returns `"status": "ok"`
   - Verifies `/` returns app info
   - Creates a task via `POST /tasks` and confirms it was saved
   - Lists tasks via `GET /tasks` and confirms the created task appears

On failure, the pipeline automatically tears down the containers.

## Project Structure
```
ComputingToolsProject/
├── Jenkinsfile
├── README.md
└── flask-mongo-pipeline/
    ├── docker-compose.yml
    └── app/
        ├── Dockerfile
        ├── requirements.txt
        └── app.py
```
