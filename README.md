# Django DRF Project Setup Guide

## Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- PostgreSQL (>=12)
- pip (Python package manager)
- Git
- Virtualenv

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/AnuragPrajapati15/event_management_backend.git
cd your-repo
```git 

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project's root directory and add the following:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 5. Configure Database Settings (PostgreSQL)
In `settings.py`, update the `DATABASES` section:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}
```

### 6. Apply Migrations
```bash
python manage.py migrate
```

### 7. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up a superuser.

### 8. Run the Development Server
```bash
python manage.py runserver
```

#

