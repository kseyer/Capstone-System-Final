# Quick Render Deployment Guide

## Required Environment Variables on Render

Set these in your Render web service settings:

```
SECRET_KEY=your-secret-key-generate-a-random-one
DEBUG=False
DATABASE_URL=<automatically-set-by-render-when-you-link-postgresql>
```

## Build & Start Commands

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn beauty_clinic_django.wsgi:application
```

## Python Version

Set in Render dashboard or uses `runtime.txt` (Python 3.11.9)

## That's it!

Render will:
1. Install dependencies from requirements.txt
2. Collect static files
3. Run migrations
4. Start your app with Gunicorn

The RENDER_EXTERNAL_HOSTNAME is automatically set by Render and will be added to ALLOWED_HOSTS.
