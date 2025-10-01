# veralign
A AI-based CRM tool.

# Setup
## System Installation Requirements
- [Python 3.10](https://wiki.python.org/moin/BeginnersGuide/Download)
- [PostgreSQL 18.0](https://www.postgresql.org/download/)
  - 
## Python Package Requirements
- [Django 5.2](https://www.djangoproject.com/download/)
- [psycopg 3.2.10](https://www.psycopg.org/psycopg3/docs/basic/install.html#supported-systems)
- Install using:
```
pip install -r requirements.txt
```

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
Enter the `postgres` prompt (`postgres=#`) by the following commands:
```
sudo -i -u postgres
psql
```
(If psql does not successfully start, check the psql installation with `psql --version` or check that the postgres server is running with `sudo systemctl status postgresql`. If the server is not running, start it with `sudo systemctl start postgresql`.)

Create a VerAlign-associated database and local postgres user by entering the following commands:
```
CREATE DATABASE veraligndb;
CREATE USER veralignadmin WITH PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE veraligndb TO veralignadmin;
```
(Replace `<password>` with your own password to authorize access to this local database... **Important!** Remember the password, as it will be needed to authorize Django to modify the local database)

This creates a database called `veraligndb` that Django will be able to access with the password.

## Password Setup
Enter the `veralign` project directory, and create a file containing your password to the local `veraligndb` database (the `password` file is already in the `.gitignore`).
```
cd veralign
echo "<password>" >> password
```
(replace `<password>` with the actual password)

## Migrate and Start Development Server
Migrate database entries and start local server (after returning to repository root directory via `cd ..`).
```
python manage.py makemigrations
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

