# options-mi-trade-server

Options Mi Trade Server Application

https://archives.nseindia.com/content/fo/fo_mktlots.csv
https://archives.nseindia.com/content/fo/qtyfreeze.xls
https://archives.nseindia.com/content/fo/sos_scheme.xls

# DB Dev

Database name : omtradedev
User Name : omtradedev
Password : omtradedev^15*

# Virtual Environments

# Create

python -m venv env

pip freeze > ./docs/requirements.txt
pip install -r ./docs/requirements.txt

# Activate

# WIN
.\env\Scripts\activate

# ubuntu
source env/bin/activate

# Django

# Install

pip install Django

# Create a project

django-admin startproject server .

django-admin startproject api-server .

# Runing the server

python manage.py createsuperuser
python manage.py runserver

# Create a app

python manage.py startapp base
python manage.py startapp

# Migrate DB

sudo apt install mariadb-server
sudo systemctl status mariadb

sudo mysql_secure_installation
root/root

sudo dpkg -l | grep mariadb 
sudo apt-get purge mariadb-server 

python manage.py migrate
python manage.py makemigrations

# Redis

sudo apt install redis-server
redis-server --version

# launch it at start-up is

sudo systemctl enable redis-server

sudo service redis-server start
sudo service redis-server stop

redis-cli ping

# REST 


# Celery

pip install celery
pip install redis
pip install django-celery-results
pip install django-celery-beat
pip install flower

celery worker --help

celery -A server worker -l INFO --concurrency=10 --pool processes --task-events
celery -A server worker -l INFO --autoscale=5,20 --pool processes --task-events
celery -A server flower

# watch log

watch -n 1 tail <filename> 
tail -f <filename>

# Channel

pip install -U channels["daphne"]

# Run Script

# Dataload Scripts
python manage.py runscript loadScripMaster
python manage.py runscript loadExpiryAndPrice
python manage.py runscript loadUnderlying

# Test Scripts
python manage.py runscript testAngeloneLogin
python manage.py runscript testWebSocket
python manage.py runscript testAlgoOrder
python manage.py runscript algoPaperOrder

python manage.py runscript testAngeloneAPI

