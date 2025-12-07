# Deployment Instructions for Render.com

## Quick Setup (Using render.yaml)

1. **Fork/Clone this repository** to your GitHub account
2. **Go to Render Dashboard**: https://dashboard.render.com
3. **Click "New" → "Blueprint"**
4. **Connect your GitHub repository**
5. **Render will automatically detect render.yaml** and set up:
   - Web service with Python
   - PostgreSQL database
   - Environment variables

## Manual Setup

### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Name: `beauty-clinic-db`
4. Database: `beauty_clinic`
5. User: `beauty_clinic_user`
6. Plan: Free
7. Click "Create Database"
8. **Copy the Internal Database URL** (you'll need this)

### Step 2: Create Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository: `https://github.com/kseyer/Capstone-System-Final`
3. Configure:
   - **Name**: `beauty-clinic-django`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn beauty_clinic_django.wsgi:application`
   - **Plan**: Free

### Step 3: Environment Variables

Add these in Render Dashboard > Environment:

**Required:**
```bash
SECRET_KEY=<generate-a-strong-secret-key-here>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.onrender.com
DATABASE_URL=<paste-internal-database-url-here>
PYTHON_VERSION=3.11.9
```

**Optional (if using these features):**
```bash
IPROG_SMS_API_KEY=<your-sms-api-key>
EMAIL_HOST_USER=<your-email-username>
EMAIL_HOST_PASSWORD=<your-email-password>
MAILTRAP_API_TOKEN=<your-mailtrap-token>
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Run `build.sh`
   - Install dependencies
   - Collect static files
   - Run migrations
   - Start the application with Gunicorn

## Troubleshooting

### Build Fails

1. **Check build logs** in Render Dashboard
2. **Common issues**:
   - Missing environment variables (especially DATABASE_URL)
   - Python version mismatch (check runtime.txt)
   - Dependency conflicts (check requirements.txt)

### Database Connection Error

1. Make sure DATABASE_URL is set correctly
2. Use the **Internal Database URL** from your PostgreSQL database
3. Format: `postgresql://user:password@host:5432/dbname`

### Static Files Not Loading

1. Check that WhiteNoise is in MIDDLEWARE (settings.py)
2. Verify STATIC_ROOT is set to `BASE_DIR / 'staticfiles'`
3. Build command includes `collectstatic --no-input`

### Application Crashes

1. Check logs: Render Dashboard → Logs
2. Verify all required environment variables are set
3. Check DEBUG is set to False
4. Ensure ALLOWED_HOSTS includes your Render domain

## Post-Deployment

### Create Superuser

1. Go to Render Dashboard → Shell
2. Run:
   ```bash
   python manage.py createsuperuser
   ```

### Access Admin Panel

Visit: `https://<your-app-name>.onrender.com/admin/`

## Important Notes

- ✅ Free tier sleeps after 15 minutes of inactivity
- ✅ First request after sleep may take 30-60 seconds
- ✅ Database has 90-day data retention on free tier
- ✅ SSL/HTTPS is automatically provided
- ✅ Auto-deploy on git push to main branch

## Generate Strong SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(50))
```

Or use online generator: https://djecrety.ir/
