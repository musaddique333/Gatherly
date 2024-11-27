# FastAPI Auth

This repository contains a **FastAPI** application designed for scalable development and deployment. It includes Docker setup for containerization, a development environment with Docker Compose, and guidelines for local development.

## Project Structure

```
.
├── app
│   └── main.py            # Application entry point
├── Dockerfile             # Docker container setup
├── docker-compose.dev.yml # Docker Compose for development
├── .dockerignore          # Exclusions for Docker builds
├── .env.development       # Environment variables for development
├── .env.production        # Environment variables for production
├── pyproject.toml         # Python dependencies and project metadata
├── .python-version        # Python version specification
└── uv.lock                # Dependency lock file
```

---
## Using Docker

## Debugging with VS Code

For seamless debugging, set up a `.vscode/launch.json` file:

1. Create a `.vscode` folder in the root directory.
2. Inside `.vscode`, create a `launch.json` file with the following content:

    ```json
    {
      "version": "0.2.0",
      "configurations": [
        {
          "name": "Python: Remote Attach",
          "type": "python",
          "request": "attach",
          "connect": {
            "host": "localhost",
            "port": 5678
          },
          "pathMappings": [
            {
              "localRoot": "${workspaceFolder}/app",
              "remoteRoot": "/app/app"
            }
          ],
          "justMyCode": true
        }
      ]
    }
    ```

3. Attach the debugger to the running container.

---

## Environment Variables

Here's the updated **Environment Variables** section based on your provided details:

---

### 2. Environment Variables

You can configure environment-specific variables for both **development** and **production** in the following `.env` files:

- **`.env.development`**: Development-specific variables.
- **`.env.production`**: Production-specific variables.

#### **Development Environment (`.env.development`)**

```dotenv
# JWT settings
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email verification credentials
SMTP_SERVER=
SMTP_PORT=587  # NOTE: Use 465 for SSL
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
RECOVERY_CODE=

# Users Database credentials
DB_USER=postgres
DB_PASSWORD=test
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres

# FastAPI
DEBUG=1
```

#### **Production Environment (`.env.production`)**

```dotenv
# JWT settings
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email verification credentials
SMTP_SERVER="smtp.example.com"
SMTP_PORT=587  # NOTE: Use 465 for SSL
SMTP_USER="your_email@example.com"
SMTP_PASSWORD="your_password"
EMAIL_FROM="your_email@example.com"

# Users Database credentials
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
```

---

#### **Explanation of Variables:**

- **JWT Settings**:
  - `JWT_SECRET_KEY`: The secret key used to sign the JWT tokens.
  - `JWT_ALGORITHM`: The algorithm used for JWT signing (usually `HS256`).
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for access tokens in minutes.
  
- **Email Verification Credentials**:
  - `SMTP_SERVER`: The SMTP server address for sending emails.
  - `SMTP_PORT`: The port for the SMTP server (587 for TLS, 465 for SSL).
  - `SMTP_USER`: The email address used for sending verification emails.
  - `SMTP_PASSWORD`: The password for the email address.
  - `EMAIL_FROM`: The "from" email address used in email communication.
  - `RECOVERY_CODE`: A predefined code for account recovery or password reset.

- **Users Database Credentials**:
  - `DB_USER`: The database username (e.g., `postgres`).
  - `DB_PASSWORD`: The database password.
  - `DB_HOST`: The database host (usually `localhost` in development).
  - `DB_PORT`: The database port (default `5432` for PostgreSQL).
  - `DB_NAME`: The database name (e.g., `postgres`).

- **FastAPI**:
  - `DEBUG`: A flag to enable or disable debug mode (set to `1` in development).

Ensure sensitive data is not committed to version control by including `.env` files in `.gitignore`.

### 3. Building and Running the Application
Docker simplifies the development workflow. Use **Docker Compose** for managing services in the development environment.

- **To build and run:**
  ```bash
  docker compose -f docker-compose.dev.yml up --build
  ```

- **To stop and clean up:**
  ```bash
  docker compose -f docker-compose.dev.yml down --volumes --remove-orphans --rmi all
  ```

---


## **!!!Installing UV if Developing Without DOCKER**

UV can be installed using multiple methods depending on your operating system. Here are the recommended approaches:

**macOS and Linux:**
- Install UV using the official standalone installer:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

**Windows:**
- Install UV using the official standalone installer:
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
For more installation methods (e.g., Homebrew), refer to the [UV Installation Page](https://github.com/jmcdo29/uv#installation).

---

#### **Setting Up the Virtual Environment**
1. After installing UV, sync the dependencies:
   ```bash
   uv sync
   ```
   This will create a virtual environment (`.venv`) and install all dependencies listed in the `pyproject.toml` file.

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # For macOS/Linux
   .venv\Scripts\activate     # For Windows
   ```

### 2. Development Mode
Run the application locally for development.

- Activate the virtual environment:
  ```bash
  source .venv/bin/activate
  ```

- Start the application:
  ```bash
  uvicorn app.main:app --reload
  ```

---

## Contributions

Feel free to open issues or submit pull requests for improvements. Follow the project's style and structure for consistency.
