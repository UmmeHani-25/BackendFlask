# How to Run the FlaskCar Project

## 1. Clone the Repository

```bash
git clone https://github.com/UmmeHani-25/BackendFlask.git
cd BackendFlask
````

---

## 2. Create and Activate Virtual Environment

python3 -m venv venv
.\venv\Scripts\activate.ps1   


## 3. Install Dependencies

pip install -r requirements.txt


## 4. Initialize the Database


flask db init
flask db migrate
flask db upgrade


## 5. Start Redis Server

### If using WSL:

sudo service redis-server start


## 6. Start Celery

### Terminal 1: Celery Worker

celery -A app.tasks.celery_app.celery worker --loglevel=info --pool=solo


### Terminal 2: Celery Beat


celery -A app.tasks.celery_app.celery beat --loglevel=info


## 7. Run the Flask App

flask run


# FLASK_APP=app/app.py
# FLASK_ENV=development
# DATABASE_URL=mysql+pymysql://root:1234@localhost/flaskcar
# JWT_SECRET_KEY=K8v2P9x4mN3qL7tR5wJ1yA6cF0hB4uE9
# JWT_ACCESS_TOKEN_EXPIRES=1800
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0


# Docker env

# FLASK_APP=app/app.py
# FLASK_ENV=development
# DATABASE_URL=mysql+pymysql://root:1234@mysql:3306/flaskcar
# DB_HOST=localhost
# DB_PORT=3307
# JWT_SECRET_KEY=K8v2P9x4mN3qL7tR5wJ1yA6cF0hB4uE9
# JWT_ACCESS_TOKEN_EXPIRES=1800
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/0
