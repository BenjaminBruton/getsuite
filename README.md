NetSuite FastAPI Mock API

This project provides a persistent, full-featured Mock API Server designed to simulate the NetSuite SuiteTalk REST Web Services interface. It is built using Python, FastAPI, and SQLAlchemy (with SQLite) to offer realistic latency and state persistence across restarts.

Use this mock environment for local development, integration testing, and front-end development when access to a live NetSuite sandbox is unavailable or unnecessary.

🚀 Getting Started

Follow these steps to pull the repository, set up your isolated environment, and run the server locally.

Prerequisites

You must have Python 3.9+ and Git installed on your system.

1. Clone the Repository

First, use Git to clone the repository to your local machine:

git clone [https://github.com/BenjaminBruton/getsuite.git](https://github.com/BenjaminBruton/getsuite.git)
cd getsuite


2. Set Up the Virtual Environment (venv)

It is highly recommended to use a virtual environment to isolate project dependencies from your global Python installation.

Create the environment:

python3 -m venv venv


Activate the environment:

macOS / Linux:

source venv/bin/activate


Windows (Command Prompt):

venv\Scripts\activate


Install dependencies: This installs FastAPI, Uvicorn, and SQLAlchemy.

pip install -r requirements.txt


3. Run the API Server

The application uses Uvicorn to serve the FastAPI application.

Start the server:

uvicorn mock_netsuite_api:app --reload


(The --reload flag is optional but useful for development, as it restarts the server automatically when code changes.)

Access the API: The server will typically be available at:

Base URL: http://127.0.0.1:8000

4. View Interactive Documentation (Swagger UI)

FastAPI automatically generates comprehensive API documentation. Use this interface to test all endpoints interactively:

Documentation URL: http://127.0.0.1:8000/docs

<img width="1445" height="710" alt="Screenshot 2025-11-15 at 10 12 48 PM" src="https://github.com/user-attachments/assets/fcbdb664-8540-47f0-9649-644edb55e39f" />
<img width="1447" height="456" alt="Screenshot 2025-11-15 at 10 13 00 PM" src="https://github.com/user-attachments/assets/5f200d94-c4b5-403c-bda2-4690f67a4de2" />

🛠️ API Endpoints Reference

The following endpoints simulate the NetSuite SuiteTalk REST Web Services structure. The database state is saved to a file named netsuite_mock.db and persists across server restarts.

Method

Endpoint

Description

Status Codes

POST

/services/rest/record/v1/customer

Creates a new Customer record.

201 Created

GET

/services/rest/record/v1/customer

Retrieves all Customer records (collection).

200 OK

GET

/services/rest/record/v1/customer/{id}

Retrieves a single Customer record.

200 OK, 404 Not Found

PUT

/services/rest/record/v1/customer/{id}

Updates a Customer (e.g., sets status to 'On Hold').

204 No Content, 404 Not Found

DELETE

/services/rest/record/v1/customer/{id}

Deletes a Customer record.

204 No Content, 404 Not Found

POST

/services/rest/record/v1/salesorder

Creates a new Sales Order record.

201 Created, 400 Bad Request (if Customer ID is missing)

PUT

/services/rest/record/v1/salesorder/{id}

Updates a Sales Order (e.g., sets status to 'Billed').

204 No Content, 404 Not Found

DELETE

/services/rest/record/v1/salesorder/{id}

Deletes a Sales Order record.

204 No Content, 404 Not Found
