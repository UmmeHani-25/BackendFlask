# How to Run the FlaskCar Project

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/FlaskCar.git
cd FlaskCar
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
