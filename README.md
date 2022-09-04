

# Web Application for PCTO Orientation Activities Management

This is a group project for the **Database Fundamentals** course at the **University of Venice**. The project is a web application designed to manage orientation activities (PCTO) for DAIS, providing tools for students and teachers to register, manage courses, and track participation.

![20220928_17h54m24s_grim](https://github.com/user-attachments/assets/f10e56b0-be7b-4aab-8bff-9d7b3e9deec7)

## Features
- User roles: Admin, Professor, Student.
- Course management: Creation, registration, and participation tracking for PCTO courses.
- Local SQLite or remote PostgreSQL database integration.

## Database Setup
To initialize the database, use the provided SQL script (`backup_database.txt`) or configure the `initialize_db_sqlite()` function in `database.py` to set up a local SQLite database.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
    flask run
   ```

