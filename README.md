# Campus Lost & Found

A centralized Django web application for reporting, searching, and recovering lost or found items on campus.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Report Lost Items**: Students can report items they've lost
- **Report Found Items**: Students can report items they've found
- **Browse & Search**: Search and filter through all reports
- **User Dashboard**: View and manage your own reports
- **Admin Moderation**: Admin interface for moderating reports

## Tech Stack

- **Backend**: Django 6.0.3
- **Database**: SQLite (development)
- **Frontend**: Server-rendered Django templates
- **Styling**: Custom CSS
- **Image Handling**: Pillow

## Project Structure

```
campus_lost_found/
├── config/                 # Project settings and main URLs
├── accounts/               # User authentication
├── reports/                # Core lost & found functionality
├── templates/              # Shared templates
├── static/                 # CSS, JS, images
├── media/                  # User-uploaded files
└── manage.py
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd campus_lost_found
```

### 2. Create Virtual Environment

```bash
python -m venv campus_venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
campus_venv\Scripts\activate
```

**macOS/Linux:**
```bash
source campus_venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

## Usage

### For Students

1. **Register** an account at `/accounts/register/`
2. **Login** at `/accounts/login/`
3. **Report a lost item** at `/reports/lost/new/`
4. **Report a found item** at `/reports/found/new/`
5. **Browse reports** at `/reports/`
6. **View your reports** at `/reports/mine/`

### For Administrators

1. Access admin panel at `/admin/`
2. Moderate reports, manage users, and handle categories

## Team Roles

- **Person 1**: Foundation, authentication, integration
- **Person 2**: Models, forms, CRUD operations
- **Person 3**: Search, filtering, testing, polish


## Common Commands

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Check for issues
python manage.py check
```
