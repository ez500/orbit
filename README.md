# veralign
A AI-based CRM tool.

# Setup
## System Installation Requirements
- [Python 3.10 or later](https://wiki.python.org/moin/BeginnersGuide/Download)
- [PostgreSQL 18.0](https://www.postgresql.org/download/)

## Python Package Requirements
- [Django 5.2](https://www.djangoproject.com/download/)
- [psycopg 3.2.10](https://www.psycopg.org/psycopg3/docs/basic/install.html#supported-systems)
- [Pillow 11.3.0](https://pypi.org/project/pillow/)
- Install using `pip install -r requirements.txt`.

## Python Virtual Environment (Optional)
Create a new virtual environment with the following command:
```
python -m venv .venv
```
(Replace `python` with another specific version for that specific environment)

To activate the environment, enter the following command:
Linux:
```
source .venv/bin/activate
```
Windows:
```
.venv/Scripts/activate
```
and to exit the environment, enter `deactivate`.

## Database Setup
Enter the `postgres` prompt (`postgres=#` or `psql=#`). On Windows, just open the `psql` terminal (search for service on Windows menu), or on Linux, by the following commands:
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

NOTE: If you are on Windows, you might have to enter this additional command:
```
ALTER DATABASE veraligndb OWNER TO veralignadmin;
```

## Password Setup
Enter the `veralign` project directory, and create a file containing your password to the local `veraligndb` database (the `password` file is already in the `.gitignore`). If on Windows, just create a file named `password` and type your password in the file, or use a bash environment like Git Bash for the following commands.
```
cd veralign
echo "<password>" >> password
```
(replace `<password>` with the actual password)

## .env File Setup
Make sure that you have a password file in the correct location from the previous step. Open a terminal in the Project root directory and the run the following command:
Linux (venv):
```
python env_file_maker.py
```
Windows:
```
py ./env_file_maker.py
```
A `.env` file will be created in the `veralign` folder.

## Migrate and Start Development Server
Migrate database entries and start local server (after returning to repository root directory via `cd ..`).
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Accessing Admin Interface
You need to explicitly create a superuser locally. Enter the following command:
Linux:
```
python manage.py createsuperuser
```
Windows:
```
winptl python manage.py createsuperuser
```
Enter the credentials you would like to set to access the admin interface.

# Project Structure
`veralign/` - main Django project configuration

`home/` - home application (website templates, models, URLs associated with homepage, about us page, other generic informational pages)

