# Render Deployment Guide

This guide will help you deploy your Beauty Clinic Django application to Render.com.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render.com account (sign up at https://render.com)

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

1. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ready for Render deployment"
   ```

2. Create a repository on GitHub and push your code:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

### Step 2: Create a PostgreSQL Database on Render

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `beauty-clinic-db` (or any name you prefer)
   - **Database**: `beauty_clinic`
   - **User**: `beauty_clinic_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click "Create Database"
5. **Important**: Note down the **Internal Database URL** (you'll need this)

### Step 3: Create a Web Service on Render

1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `beauty-clinic-django` (or your preferred name)
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or specify if your Django app is in a subdirectory)
   - **Environment**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn beauty_clinic_django.wsgi:application`

### Step 4: Configure Environment Variables

In your Render Web Service dashboard, go to "Environment" tab and add:

**Required Variables:**
- `SECRET_KEY`: Generate a new secret key (you can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com` (Render will provide this after first deploy)
- `DATABASE_URL`: Use the Internal Database URL from Step 2

**Optional Variables (if you want to change defaults):**
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `IPROG_SMS_API_KEY`: Your SMS API key
- `SMS_ENABLED`: `True` or `False`
- `EMAIL_HOST`: Your email host
- `EMAIL_HOST_USER`: Your email username
- `EMAIL_HOST_PASSWORD`: Your email password
- `MAILTRAP_API_TOKEN`: Your Mailtrap token

### Step 5: Link Database to Web Service

1. In your Web Service dashboard, go to "Environment" tab
2. Under "Environment Variables", click "Link Database"
3. Select your PostgreSQL database created in Step 2
4. Render will automatically add the `DATABASE_URL` variable

### Step 6: Deploy

1. Click "Save Changes" in your Web Service
2. Render will automatically start building and deploying
3. Monitor the build logs for any errors
4. Once deployed, your app will be available at `https://your-app-name.onrender.com`

### Step 7: Run Initial Setup (First Deploy Only)

After the first successful deployment, you may need to:

1. Create a superuser (via Render Shell or SSH):
   - Go to your service → "Shell"
   - Run: `python manage.py createsuperuser`

2. Update ALLOWED_HOSTS with your actual Render URL:
   - Go to Environment Variables
   - Update `ALLOWED_HOSTS` to include your full Render domain

### Step 8: Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Update your OAuth 2.0 Client ID settings
3. Add authorized redirect URI: `https://your-app-name.onrender.com/accounts/google/login/callback/`

## Using render.yaml (Alternative Method)

If you prefer using the `render.yaml` file:

1. Make sure your code is pushed to GitHub
2. In Render Dashboard, click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect and use `render.yaml`
5. Review and apply the configuration

## Important Notes

1. **Static Files**: WhiteNoise is configured to serve static files. Make sure `collectstatic` runs during build.

2. **Media Files**: Currently, media files are stored locally. For production, consider using:
   - AWS S3
   - Cloudinary
   - Or Render's persistent disk (paid plans)

3. **Database Migrations**: Migrations run automatically during build via `build.sh`

4. **Free Tier Limitations**:
   - Services spin down after 15 minutes of inactivity
   - Limited resources
   - Consider upgrading for production use

5. **Environment Variables**: Never commit sensitive keys to git. Always use environment variables.

## Troubleshooting

- **Build Fails**: Check build logs for missing dependencies or errors
- **Database Connection Issues**: Verify `DATABASE_URL` is correctly set
- **Static Files Not Loading**: Ensure `collectstatic` runs successfully
- **500 Errors**: Check logs in Render dashboard, verify all environment variables are set

## Next Steps

- Set up custom domain (if needed)
- Configure email service for production
- Set up automated backups
- Monitor application logs
- Set up error tracking (Sentry, etc.)

