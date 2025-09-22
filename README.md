# veralign
A AI-based CRM tool.

## Django Project Setup

This repository now contains a basic Django template for the Veralign CRM system.

### Features
- Django 4.2.7 project structure
- Basic CRM app with home and dashboard views
- Responsive HTML templates with modern styling
- Admin interface setup
- SQLite database configuration
- Basic URL routing

### Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Open your browser and navigate to:
   - Home page: http://127.0.0.1:8000/
   - Dashboard: http://127.0.0.1:8000/dashboard/
   - Admin interface: http://127.0.0.1:8000/admin/

### Project Structure
- `veralign/` - Main Django project configuration
- `crm/` - CRM application with views, templates, and URLs
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore file for Python/Django projects

### Default Admin Credentials
- Username: admin
- Email: admin@veralign.com
- Password: admin123

**Note**: Change these credentials in production!
