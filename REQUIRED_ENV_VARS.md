# REQUIRED Environment Variables for Render

## Add these in Render Dashboard → Environment:

### CRITICAL (Must Have):
```
SECRET_KEY=django-insecure-CHANGE-THIS-TO-RANDOM-STRING-50-CHARS
DEBUG=False
DATABASE_URL=<auto-populated-when-you-link-postgresql-database>
```

### OPTIONAL (Remove if not using):
You can REMOVE all the email/SMS variables if you don't need them:
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- EMAIL_USE_TLS
- DEFAULT_FROM_EMAIL
- MAILTRAP_API_TOKEN
- IPROG_SMS_API_KEY
- SMS_ENABLED
- SMS_SENDER_ID

The app will work fine without email/SMS - those are optional features.

## Generate SECRET_KEY:

Option 1 - Use Python:
```python
import secrets
print(secrets.token_urlsafe(50))
```

Option 2 - Use online generator:
https://djecrety.ir/

## Database:
Make sure you've created a PostgreSQL database in Render and linked it to your web service.
The DATABASE_URL will be auto-populated.
