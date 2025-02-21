# Obituary Writer API & ML PoC

## Overview

This project is a proof of concept (PoC) aimed at enhancing the existing Obit Writer API by integrating cutting-edge technologies for obituary generation, evaluation, and retrieval. The goal is to improve the obituary writing process by leveraging OpenAI’s GPT for text generation, PostgreSQL with `pgvector` for similarity-based searches, and a structured and scalable API.

The system is designed to streamline obituary creation using both structured and unstructured inputs, providing flexibility in writing styles while ensuring high-quality outputs. Machine learning techniques are incorporated to score and rank obituaries, offering automated quality assessment. Additionally, real-time logging, embedding-based retrieval, and API-driven interactions contribute to a robust obituary publishing workflow.

## Features

- **Obituary Generation**: Uses OpenAI GPT to create structured obituaries.
- **Database Storage**: Stores obituaries in PostgreSQL.
- **Embedding & Vector Search**: Enables similarity-based retrieval of obituaries.
- **ML-Based Scoring**: Evaluates obituary quality using OpenAI + machine learning models.
- **API Endpoints**: CRUD operations, obituary scoring, and similarity search.
- **Real-Time Evaluation & Logging**: Tracks API usage, model performance, and user feedback.

## Installation & Setup

### 1. System Requirements

- **macOS** (Apple Silicon or Intel)
- **Homebrew** (for package management)
- **Python 3.9+**
- **PostgreSQL 14+** (must be running before setup)

### 2. Install Required Applications

#### **Development Tools**

```sh
brew install git python postgresql@14
```

- **VS Code** (Recommended IDE)
- **Postman** (for API testing)
- **TablePlus** (for PostgreSQL management) - [Download](https://tableplus.com/)

### 3. Setup the Virtual Environment

```sh
cd obituary_project
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```sh
pip install -r requirements.txt
```

If `requirements.txt` is missing, manually install:

```sh
pip install openai sqlalchemy pgvector psycopg2-binary pydantic httpx python-dotenv alembic
```

### 5. Get an OpenAI API Key

To generate obituaries, you need an OpenAI API key. Follow these steps:

1. Go to [OpenAI's API page](https://platform.openai.com/signup/) and sign up for an account.
2. Navigate to the **API Keys** section under your profile settings.
3. Click **Create API Key**, then copy and save it securely.
4. Add the key to your environment variables:

```sh
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

Alternatively, add it to your `.env` file:

```sh
OPENAI_API_KEY=your_api_key_here
```

### 6. Configure Environment Variables

```sh
echo 'export DATABASE_URL="postgresql://obituary_user:password@localhost/obituary_db"' >> ~/.zshrc
source ~/.zshrc
```

Alternatively, create a `.env` file:

```sh
DATABASE_URL=postgresql://obituary_user:password@localhost/obituary_db
```

To verify the environment variable is set, run:

```sh
echo $DATABASE_URL
```

If it returns an empty value, restart your terminal or run:

```sh
source ~/.zshrc
```

### 7. Setup PostgreSQL & TablePlus

#### **Start PostgreSQL**

```sh
brew services start postgresql@14
```

#### **Create Database & Enable Vector Extension**

```sh
psql -U $(whoami) -d postgres -c "CREATE DATABASE obituary_db;"
psql -U $(whoami) -d obituary_db -c "CREATE EXTENSION vector;"
```

#### **Setup TablePlus for PostgreSQL Management**

1. Open TablePlus.
2. Click **Create a New Connection**.
3. Select **PostgreSQL**.
4. Fill in the details:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **User**: Your macOS username
   - **Password**: Leave empty if not set
   - **Database**: `obituary_db`
5. Click **Connect** to verify the connection.

### 8. Initialize and Migrate Database with Alembic

#### **Initialize Alembic**

```sh
alembic init alembic
```

This creates an `alembic.ini` file and an `alembic/` directory.

#### **Configure Alembic**

Edit `alembic.ini` and update the `sqlalchemy.url` setting:

```
sqlalchemy.url = ${DATABASE_URL}
```

Edit `alembic/env.py` and set `target_metadata`:

```python
from app.core.models import Base  # Import your SQLAlchemy models
target_metadata = Base.metadata
```

#### **Generate Migrations**

```sh
alembic revision --autogenerate -m "Initial migration"
```

#### **Apply Migrations**

```sh
alembic upgrade head
```

### 9. Test Database Connection

```sh
python -c "from database import engine; print(engine.connect())"
```

If successful, move to API testing.

## Running the API

```sh
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Endpoint                             | Description                                   |
| ------ | ------------------------------------ | --------------------------------------------- |
| POST   | /generate_obituary                  | Generate and store a new obituary            |
| GET    | /obituaries                         | Retrieve stored obituaries                   |
| GET    | /obituaries/{id}                    | Fetch a single obituary by ID                |
| POST   | /score_obituary                     | Evaluate obituary quality                    |
| GET    | /search_obituaries                  | Search for similar obituaries                |
| POST   | /generate_sample_scratchpad_obit    | Generate sample obituaries using scratchpad  |
| POST   | /generate_embeddings/{obituary_id}  | Generate embeddings for a specific obituary  |
| POST   | /generate_embeddings                | Generate embeddings for all missing entries  |

## API Documentation

Swagger documentation is available at:

```
http://127.0.0.1:8000/docs
```

Use this URL to test endpoints interactively.

## Next Steps

- **API Testing in Postman**
- **UI Development**
- **ML Integration for Ranking & Scoring**

