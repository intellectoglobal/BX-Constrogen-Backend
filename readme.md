pip install virtualenv
python -m venv env
.\env\Scripts\activate

install postgres from https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
<Store the password >
Open PgAdmin
Create Database By right clicking on Databases
Provide DB name as BuilderIQ

open psql command prompt
login using following setup
Server [localhost]: localhost
Database [postgres]: BuilderIQ
Port [5432]: 5432
Username [postgres]: postgres
Password for user postgres: <Stored the password>

Run the postgres command
create user builderiq_user with encrypted password 'someR@nd0mP@$$';
--This will create a USER role for BuilderIQ DB which is configured in BACKEND APPLICATION

pip install -r requirements.txt
python manage.py makemigrations users
python manage.py makemigrations address
python manage.py makemigrations client
python manage.py migrate
CMD TO CREATE SUPERUSER: python manage.py createsuperuser
python manage.py runserver

once application start runing
USE http://localhost:8000/swagger-ui/ to list the available APIs

You can use Postgress PGAdmin tool for database queries
