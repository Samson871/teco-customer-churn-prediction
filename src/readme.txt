## Installation Guide

Follow these steps to set up and run the project:

### 1. Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/Samson871/teco-customer-churn-prediction.git
cd teco-customer-churn-prediction
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to isolate dependencies:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
Initialize the SQLite database for user authentication:
```bash
python -c "from app import db; db.create_all()"
```

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

---

### Deployment
For production, use a WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```