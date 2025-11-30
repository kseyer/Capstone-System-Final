# 🛠️ Fix Remaining Issues: Google Sign-In, Password Reset & More

## ✅ Issues Fixed in This Update

1. **Booking Error** (MultipleObjectsReturned) - ✅ FIXED
2. **Reschedule Policy** - ✅ Already implemented
3. **Cancellation Policy** - ✅ Already implemented

## ⚠️ Issues Still Needing Manual Configuration

### 1. Google Sign-In Fix

**Issue**: Google OAuth not working properly on Render

**Solution**: Update Google Cloud Console with correct redirect URIs

#### Steps to Fix Google Sign-In:

**Step 1: Update Google Cloud Console**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Click on your **OAuth 2.0 Client ID**
5. Add these redirect URIs under **Authorized redirect URIs**:

```
https://capstone-system-final.onrender.com/accounts/google/login/callback/
https://capstone-system-final.onrender.com/accounts/google/login/callback
```

**Step 2: Update Environment Variables on Render**

In Render Dashboard:
1. Go to your web service
2. Click **Environment**
3. Add/Update these variables:

```
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
```

**Step 3: Test Google Sign-In**

Visit: https://capstone-system-final.onrender.com/accounts/login/

### 2. Password Reset Fix

**Issue**: Password reset emails not being sent on Render

**Solution**: Configure proper email settings

#### Steps to Fix Password Reset:

**Option A: Use Mailtrap (Current Configuration)**

1. Go to [Mailtrap](https://mailtrap.io/)
2. Get your SMTP credentials
3. Update these environment variables on Render:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_mailtrap_username
EMAIL_HOST_PASSWORD=your_mailtrap_password
DEFAULT_FROM_EMAIL=Skinovation Beauty Clinic <noreply@skinovation.com>
```

**Option B: Use Gmail SMTP (Recommended for Production)**

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update these environment variables on Render:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=Skinovation Beauty Clinic <your_email@gmail.com>
```

### 3. Booking Policy Implementation

**✅ Already Implemented**: Patients cannot book at 6:00 PM (last option is 1 hour before closed time)

**Code Location**: `appointments/views.py` lines 259-269

### 4. Reschedule Policy Implementation

**✅ Already Implemented**: Patients cannot reschedule when appointment is within the same day

**Code Location**: `appointments/views.py` lines 1138-1150 and 1219-1222

### 5. Cancellation Policy Implementation

**✅ Already Implemented**: Patients cannot cancel when appointment is within 2 days

**Code Location**: `appointments/views.py` lines 963-971, 1040-1042

## 📋 Summary of All Policies

### Booking Policy:
- ✅ Last booking time: 5:00 PM (1 hour before 6:00 PM closing)
- ✅ Cannot book in the past
- ✅ Cannot book on closed days

### Reschedule Policy:
- ✅ Cannot reschedule within the same day of appointment
- ✅ Cannot reschedule to past dates
- ✅ Cannot reschedule to closed days

### Cancellation Policy:
- ✅ Cannot cancel within 2 days of appointment
- ✅ Must provide reason for cancellation
- ✅ Owner approval required for all cancellations

## 🚀 Deployment Instructions

**After making configuration changes:**

1. Go to Render Dashboard
2. Click on your service: **capstone-system-final**
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait 5-10 minutes for deployment to complete

## 🧪 Testing Checklist

**After deployment, test these features:**

1. **Google Sign-In**:
   - Visit: https://capstone-system-final.onrender.com/accounts/login/
   - Click "Sign in with Google"
   - Should redirect to Google OAuth

2. **Password Reset**:
   - Visit: https://capstone-system-final.onrender.com/accounts/password-reset/
   - Enter email and submit
   - Should receive password reset email

3. **Booking Policy**:
   - Try booking at 6:00 PM - should show error
   - Try booking in past - should show error

4. **Reschedule Policy**:
   - Try rescheduling same-day appointment - should show error

5. **Cancellation Policy**:
   - Try canceling within 2 days - should show error

## 🆘 Troubleshooting

### If Google Sign-In Still Doesn't Work:

1. Check Google Cloud Console redirect URIs match exactly
2. Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
3. Check Render logs for OAuth errors

### If Password Reset Still Doesn't Work:

1. Check email configuration in Render environment variables
2. Verify SMTP credentials are correct
3. Check Render logs for email sending errors

### If Policies Don't Work:

1. Check Render logs for error messages
2. Verify the latest code has been deployed
3. Check for any database migration issues

## 📝 Additional Notes

All policy implementations are already in the codebase:
- Booking policies in `appointments/views.py` (book_service function)
- Reschedule policies in `appointments/views.py` (request_reschedule function)
- Cancellation policies in `appointments/views.py` (request_cancellation function)

The only remaining issues are configuration-based and require updating:
1. Google OAuth redirect URIs in Google Cloud Console
2. Email settings in Render environment variables

Once these configurations are updated, all features should work correctly on your Render deployment.
