# veralign
A AI-based CRM tool.

# Setup
## System Installation Requirements
- [Python 3.10](https://wiki.python.org/moin/BeginnersGuide/Download)
- [MySQL 8.4](https://dev.mysql.com/doc/refman/8.4/en/installing.html)
  - **Important!** Remember the password you set when setting up the MySQL database, it will be needed to authorize Django to modify the local database

## Python Package Requirements
- [Django 5.2](https://www.djangoproject.com/download/)
- [mysqlclient 2.2](https://pypi.org/project/mysqlclient/)

## Python Virtual Environment (Optional)
Create a new virtual environment with the following command:
```
python -m venv .venv
```
(Replace `python` with another specific version for that specific environment)

To activate the environment, enter the following command:
```
source .venv/bin/activate
```
and to exit the environment, enter `deactivate`.

## Database Setup
Enter the database as a root user by the following command:
```
mysql -u root -p
```
Enter the password when prompted. After entering the MySQL prompt, (`mysql>`) enter the following command:
```
CREATE DATABASE veralign CHARACTER SET utf8mb4;
```
This creates a database called `veralign` that has a `utf8` character set.

## Password Setup
Enter the `veralign` project directory, and create a file containing your password to the root user login for your local MySQL database (the `password` file is already in the `.gitignore`).
```
cd veralign
echo "<PASSWORD>" >> password
```
(replace `<PASSWORD>` with your actual password to the root user login for your MySQL database)

## Migrate and Start Development Server
Migrate database entries and start local server (return to repository root directory first via `cd ..`).
```
python manage.py migrate
python manage.py runserver
```

## Accessing Admin Interface
You need to explicitly create a superuser locally. Enter the following command:
```
python manage.py createsuperuser
```
Enter the credentials you would like to set to access the admin interface.

# Project Structure
`veralign/` - main Django project configuration
`crm/` - CRM application (website templates, models, URLs)

