# Skinovation Beauty Clinic - Django Version

A comprehensive Django-based beauty clinic management system with appointment booking, service management, and patient analytics.

## 🌟 Key Features

### User Management
- **Multi-role system**: Patients, Admins, Owners, and Staff
- **Secure authentication**: Login, registration, and profile management
- **Data privacy compliant**: GDPR/Local privacy law compliant

### Core Functionality
- **Service Management**: Beauty and skincare services with categories
- **Product Management**: Skincare products with inventory tracking
- **Package Management**: Service packages with session tracking
- **Appointment System**: Online booking for services, products, and packages
- **Real-time Notifications**: Appointment updates and reminders
- **Customer Feedback**: Rating and review system

### Business Intelligence
- **Analytics Dashboard**: Revenue, patient, and service analytics
- **Patient Segmentation**: Customer classification and insights
- **Business Reporting**: Financial and operational reports

## 🛠️ Technical Stack

- **Framework**: Django 5.2.1
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Cloud Storage**: Cloudinary for permanent image storage
- **Deployment**: Ready for Heroku, Railway, Fly.io, or Render

## 🚀 Quick Deployment Options

### Option 1: Heroku (Recommended)
1. Fork this repository
2. Create Heroku account
3. Connect GitHub repository to Heroku
4. Add PostgreSQL addon
5. Set environment variables
6. Deploy!

### Option 2: Railway
1. Fork this repository
2. Sign up at Railway.app
3. Create new project from GitHub
4. Railway auto-detects Django settings
5. Add PostgreSQL database
6. Deploy with one click!

### Option 3: Fly.io
1. Install flyctl CLI
2. Run `fly launch` in project directory
3. Follow prompts to configure
4. Deploy with `fly deploy`

## ⚙️ Environment Variables Required

```bash
# Critical for security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database (provided automatically by hosting platform)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional features (can be omitted)
IPROG_SMS_API_KEY=your-sms-api-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloudinary for permanent image storage (HIGHLY RECOMMENDED)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
USE_CLOUDINARY=True
```

## 📦 Setup Instructions

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/yourusername/beauty-clinic-django.git
cd beauty-clinic-django

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver
```

### Production Deployment
1. Set all required environment variables
2. Run `python manage.py migrate`
3. Create superuser with `python manage.py createsuperuser`
4. Collect static files with `python manage.py collectstatic`

## 🔐 Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

Change these immediately after first login!

## 📞 Support
For issues or questions, please create a GitHub issue or contact the repository maintainer.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.