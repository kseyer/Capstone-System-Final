# Deployment Instructions for Render.com

## Build Configuration

### Environment Variables
Add these in Render Dashboard > Environment:

```
SECRET_KEY=<generate-a-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.onrender.com
DATABASE_URL=<automatically-provided-by-render>
```

### Build Command
```bash
./build.sh
```

### Start Command
```bash
gunicorn beauty_clinic_django.wsgi:application
```

## Database Setup

1. Create a PostgreSQL database on Render
2. Link it to your web service
3. The DATABASE_URL will be automatically added to environment variables

## Static Files

Static files are handled by WhiteNoise and will be collected during the build process.

## Important Notes

- Make sure to set DEBUG=False in production
- Generate a strong SECRET_KEY for production
- Add your domain to ALLOWED_HOSTS
- The build.sh script will run migrations automatically
