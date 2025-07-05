# Modular Asset Management Interview Project

This project is a web application that scrapes financial data from CCIL India, stores it in a database, and presents it through a web interface. It includes scripts for initial data backfilling and incremental updates.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12
- [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (for deployment)

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd modular_am
    ```

2.  **Install `uv` (if you don't have it):**
    ```sh
    # On macOS
    brew install uv
    # Other systems
    pip install uv
    ```

3.  **Create a virtual environment and install dependencies:**
    ```sh
    uv sync
    ```

4.  **Set up environment variables:**
    Copy the example environment file and update it with your database credentials and other settings.
    ```sh
    cp .env.local.example .env.local
    ```
    Then, edit `.env.local`.

5.  **Set up the database:**
    Run the database migrations to set up the necessary tables.
    ```sh
    alembic upgrade head
    ```

## Running the Application

1.  **Run the initial data backfill:**
    This script will populate the database with historical data.
    ```sh
    uv run python -m scripts.backfill_increment
    ```

2.  **Start the web application:**
    ```sh
    uv run python app.py
    ```
    The application will be available at `http://127.0.0.1:8050`.

## Scripts

-   [`app.py`](app.py): The main Dash web application.
-   [`increment.py`](increment.py): A script to scrape the latest data and update the database.
-   [`scripts/backfill_increment.py`](scripts/backfill_increment.py): A script to perform a one-time backfill of historical data.

## Scheduled Tasks (Cron Job)

To keep the data up-to-date automatically, you can set up a cron job to run the `backfill_increment.py` script periodically.

1.  Open your crontab for editing:
    ```sh
    crontab -e
    ```

2.  Add the following line to run the script every hour. Make sure to replace `<YOUR_ABSOLUTE_PATH>` with the absolute path to the project directory.
    ```
    0 * * * * cd <YOUR_ABSOLUTE_PATH>/modular_am && .venv/bin/python -m scripts.backfill_increment >> cron.log 2>&1
    ```
3. :wq ENTER

## Deployment to Azure

1.  **Log in to Azure:**
    ```sh
    az login
    ```

2.  **Deploy the web application:**
    Choose a unique name for your application.
    ```sh
    az webapp up -n your-unique-app-name --runtime "PYTHON:3.12"
    ```
    (Deployed solution example: https://dash-asz.azurewebsites.net/)