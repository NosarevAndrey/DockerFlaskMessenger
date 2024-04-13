# Flask/PostgreSQL Simple Messenger App

This is a simple messenger app built using Flask for the backend and PostgreSQL for the database.

## Running the App

To run the app locally, follow these steps:

1. Make sure you have Docker installed on your system.

2. Clone this repository:
```
git clone https://github.com/NosarevAndrey/DockerFlaskMessenger
```
3. Start the services using Docker Compose:
```
docker-compose up -d --build
```
4. Once the services are up and running, you can access the web app at [http://localhost:3000/](http://localhost:3000/).

## Accessing pgAdmin

pgAdmin is used to manage the PostgreSQL database. You can access it at [http://localhost:8080/](http://localhost:8080/).

Default credentials for pgAdmin:
- Email: admin@example.com
- Password: admin

## Database Connection

To connect to the database in pgAdmin, use the following credentials:
- Host: db
- Port: 5432
- Username: admin
- Password: admin

