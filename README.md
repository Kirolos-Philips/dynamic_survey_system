# Dynamic Survey System 📊

A professional platform for building and managing smart surveys. This system allows you to create complex forms that adapt to user answers, handle bulk email invitations, and generate optimized data reports in the background.

---

## 📖 How to Use the System

The project is designed with a clear workflow for managing the lifecycle of a survey:

### 1. Building your Survey
Using the **Admin Dashboard**, you can define your survey structure:
- **Sections:** Group related questions together.
- **Questions:** Add various types of questions (Text, Multiple Choice, Checkboxes, Dates, etc.).
- **Smart Logic:** Set rules to show or hide questions based on previous answers. For example, if a user picks a specific option, you can trigger a follow-up question automatically.

### 2. Sending Invitations
Once your survey is ready:
- You can upload or provide a list of participant emails.
- Each participant receives a unique secure link to access the survey.

### 3. Collecting & Monitoring Data
As participants fill out the survey:
- Responses are validated and saved in real-time.
- You can monitor the progress of each submission and invitation batch through the dashboard.
- Every change is logged for security and auditing purposes.

### 4. Exporting Reports
When you are ready to analyze the data:
- Use the **Reports** tool to request a data export.
- The system processes the data in the background (even for thousands of records) and provides a clean CSV file.
- The export is optimized to include all dynamic questions as organized columns.

---

## 🛠 Project Setup

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Quick Start
1. **Clone and Enter the Project:**
   ```bash
   git clone https://github.com/Kirolos-Philips/dynamic_survey_system.git
   cd dynamic_survey_system
   ```

2. **Launch and Setup:**
   ```bash
   make build
   make up
   make migrate
   make createsuperuser
   ```

3. **Access Links:**
   - **Admin Dashboard:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - **Swagger API Docs:** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
   - **Redoc API Docs:** [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)
   - **Email Preview (Mailpit):** [http://localhost:8025/](http://localhost:8025/)
   - **System Monitoring (Flower):** [http://localhost:5555/](http://localhost:5555/)

---

## 🚀 Technical Stack

- **Core:** Python 3.12 / Django 6.0 / DRF
- **Task Processing:** Celery & Redis (Emails, Exports, Logic processing)
- **Database:** PostgreSQL (with Audit Logging)
- **Monitoring:** Flower (for background tasks)
- **Export Engine:** Django Import-Export

---

## 🛠 Utility Commands (Makefile)

The `Makefile` provides shortcuts for almost every task in the project. You can run them from the root directory:

| Command | Description |
| :--- | :--- |
| **`make build`** | Build or rebuild the Docker containers. |
| **`make rebuild`** | Force a rebuild of containers without using cache. |
| **`make up`** | Start the system in the background. |
| **`make down`** | Stop the system and remove containers. |
| **`make restart`** | Restart all services. |
| **`make logs`** | View live logs from all containers (add service name to filter, e.g., `make logs django`). |
| **`make migrate`** | Apply database migrations. |
| **`make makemigrations`**| Detect changes and create new migration files. |
| **`make createsuperuser`**| Create an admin user for the dashboard. |
| **`make shell`** | Open a Python shell inside the Django environment. |
| **`make seed-surveys`** | Load a demo survey with pre-defined rules (Local environment only). |
| **`make test`** | Run the automated test suite. |
| **`make lint`** | Run the Ruff linter to check code quality. |
| **`make bash`** | Open a terminal (bash) inside the Django container. |
| **`make swarm-deploy`** | Deploy stack to swarm using `compose/swarm.yml`. |
| **`make swarm-down`** | Remove stack from swarm. |

---

## ☁️ Docker Swarm Deployment

This project includes a production-ready Swarm configuration with scaling, rolling updates, and health checks.

### Setup & Deploy
1. **Initialize Swarm (First time only):**
   ```bash
   docker swarm init
   ```

2. **Build Production Images:**
   ```bash
   make build ENV=production
   ```

3. **Deploy to Swarm:**
   ```bash
   make swarm-deploy
   ```
   *This deploys 3 Django replicas, 1 Postgres (pinned to manager), 1 Redis, and Celery workers.*

4. **Verify Deployment:**
   ```bash
   docker stack ps dynamic_survey_system
   ```

5. **Stop & Remove Stack:**
   ```bash
   make swarm-down
   ```

---

## 📁 Project Structure

```text
├── apps/
│   ├── surveys/        # Question & logic management
│   ├── submissions/    # Answer collection & export resource
│   ├── communications/ # Invitations & email engine
│   ├── users/          # Permissions & roles
│   └── reports/        # Export task tracking
```
