# Columbia COMS W4111.001 - Introduction to Databases Webserver

## Overview
This Flask web application is designed as part of the Columbia University's course COMS W4111.001 - Introduction to Databases. It provides a web interface for interacting with a database, showcasing different routes and SQL queries to handle real-world data in a database management context.

## Prerequisites
Before running this application, ensure you have the following installed:
- Python 3
- Flask
- SQLAlchemy
- A PostgreSQL database server

## Installation
1. Clone the repository or download the source code.
2. Navigate to the project directory.
3. Install the required Python dependencies:
   ```
   pip install flask sqlalchemy
   ```

## Configuration
Before running the server, you must configure the database connection. Replace the `DATABASEURI` in the script with your actual database URI, following the format:
```
postgresql://USER:PASSWORD@HOST/DATABASE
```

## Running the Server
To start the server, run the following command in your terminal:
```
python3 server.py
```
After running the server, access the web interface at:
```
http://localhost:8111
```

## Features
The application supports various features and routes, including:
- Displaying information from the database on the home page.
- Searching through different data domains like Releases, Songs, Artists, Labels, Genres, and Instruments.
- Viewing detailed information about releases, songs, artists, labels, genres, and instruments.
- Adding new data to the database through a specific route.

## Debugging
For debugging, you may find it useful to use a debugger like `pdb`. Read about debugging Flask applications online for more guidance.

## Notes
- This application is configured with a dummy database URI and needs to be updated with actual credentials.
- The application's routes and SQL queries are designed for a specific database schema. Ensure your database schema matches the expected structure.
