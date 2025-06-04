Data_Api2 Project
This project serves as a foundational Django application, containerized using Docker. It features a custom user model with email as the username and utilizes a PostgreSQL database. It's set up with basic configurations, including a Django admin interface for user management, and is ready for further development of specific features or APIs.

Features
Backend Framework: Django
Custom User Model: Uses email as the unique identifier (username) and includes a manager for user creation.
Database: PostgreSQL, configured for the application.
Containerization: Dockerized environment using Docker and Docker Compose for consistent development and deployment.
Admin Interface: Basic Django admin interface available for user management.
Code Quality: Includes linting tools and CI checks via GitHub Actions to maintain code standards.
Prerequisites
Before you begin, ensure you have the following software installed on your local machine:

Git
Docker
Docker Compose
Setup and Installation
Follow these steps to get the project up and running on your local machine:

Clone the repository:

git clone https://github.com/RamziFR/Data_Api2.git # Replace with the actual URL if different
cd Data_Api2
Environment Variables: The application uses environment variables for database configuration. These are pre-configured in the docker-compose.yml file for local development:

DB_HOST: db
DB_NAME: devdb
DB_USER: devuser
DB_PASSWORD: changeme
The PostgreSQL service in docker-compose.yml also uses these credentials (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD). If you need to customize these (e.g., for a different environment), you can modify them directly in the docker-compose.yml or use an .env file by uncommenting/adding env_file: .env to the app service in docker-compose.yml and creating an .env file in the project root.

Build and Run with Docker Compose: This command will build the Docker images (if they don't exist) and start the application and database services in detached mode.

docker-compose up -d --build
The app service command in docker-compose.yml automatically runs database migrations (python manage.py migrate) upon startup after ensuring the database is ready.

Create a Superuser: To access the Django admin interface, you'll need a superuser account.

docker-compose exec app python manage.py createsuperuser
Follow the prompts to set up your email, name (if prompted), and password.

Accessing the Application: Once the services are running, you can access:

Django Admin Panel: http://localhost:8080/admin/
(Note: The port is 8080 as configured in docker-compose.yml)

Running Tests
The project is configured with tests that can be run using Docker Compose. The command also ensures the database is ready and migrations are applied before executing the test suite.

To run the tests:

docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate && python manage.py test"
This command executes the tests within a temporary container based on the app service configuration. The --rm flag ensures the container is removed after the tests complete.

Project Structure
Here's a brief overview of the main directories and key files in the project:

Data_Api2/
├── .github/                     # GitHub Actions workflows (e.g., CI checks)
├── app/                         # Main Django project directory
│   ├── app/                     # Django project settings, URLs, ASGI/WSGI configs
│   │   ├── settings.py          # Django settings for the project
│   │   ├── urls.py              # Root URL configurations
│   │   └── ...
│   ├── core/                    # A Django app within the project
│   │   ├── models.py            # Defines database models (e.g., Custom User). Note: Contains a typo 'UseManager' which should likely be 'UserManager'.
│   │   ├── admin.py             # Admin site configurations for 'core' models
│   │   ├── views.py             # Views for the 'core' app (currently basic)
│   │   ├── management/          # Custom Django management commands
│   │   └── migrations/          # Database migration files for the 'core' app
│   ├── manage.py                # Django's command-line utility
│   └── ...
├── Dockerfile                   # Defines the Docker image for the application
├── docker-compose.yml           # Configures Docker services for local development (app, db)
├── requirements.txt             # Python dependencies for the application
├── requirements.dev.txt         # Python dependencies for development (e.g., testing, linting)
└── README.md                    # This file
end
