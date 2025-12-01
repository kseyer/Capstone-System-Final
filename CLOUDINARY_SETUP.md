# Cloudinary Setup for Persistent Media Storage

## Problem Solved
On Render's free tier, uploaded images (service images, product images, profile pictures) are deleted when the app redeploys because the filesystem is ephemeral. This guide sets up **Cloudinary** - a free cloud storage service that keeps your images persistent.

## What Was Changed

### 1. Patient Limit Updated
- **Changed from 762 to 500 patients**
- Patient IDs will be sequential from 1-500
- Updated files:
  - `accounts/management/commands/limit_patients.py` - Default changed to 500
  - `build.sh` - Deployment script now limits to 500 patients

### 2. Cloudinary Integration Added
- **Added persistent cloud storage for all uploaded images**
- Images will now stay even after redeployments
- Updated files:
  - `requirements.txt` - Added `django-cloudinary-storage` and `cloudinary`
  - `beauty_clinic_django/settings.py` - Configured Cloudinary storage

## Step 1: Create Free Cloudinary Account

1. **Go to Cloudinary**: https://cloudinary.com/users/register_free
2. **Sign up** with your email (it's completely free)
3. **Verify your email** and log in to the dashboard

## Step 2: Get Your Cloudinary Credentials

After logging in to Cloudinary dashboard:

1. Go to **Dashboard** (it should open by default)
2. You'll see your **Account Details** at the top:
   ```
   Cloud Name: your_cloud_name
   API Key: 123456789012345
   API Secret: abcdefghijklmnopqrstuvwxyz
   ```
3. **Copy these three values** - you'll need them in the next step

## Step 3: Configure Cloudinary on Render

1. **Go to your Render Dashboard**: https://dashboard.render.com/
2. **Click on your web service**: `capstone-system-final`
3. **Click "Environment"** in the left sidebar
4. **Add these environment variables** by clicking "Add Environment Variable":

   | Key | Value | Example |
   |-----|-------|---------|
   | `USE_CLOUDINARY` | `True` | `True` |
   | `CLOUDINARY_CLOUD_NAME` | Your cloud name from Cloudinary | `dj12ab34cd` |
   | `CLOUDINARY_API_KEY` | Your API key from Cloudinary | `123456789012345` |
   | `CLOUDINARY_API_SECRET` | Your API secret from Cloudinary | `abcdefghijklmnopqrstuvwxyz` |

5. **Click "Save Changes"** at the bottom

## Step 4: Deploy the Updated Code

### Option A: Manual Deploy (Recommended)

1. **In Render Dashboard**, go to your web service
2. **Click "Manual Deploy"** → **"Deploy latest commit"**
3. **Wait for deployment to complete** (usually 2-5 minutes)

### Option B: Git Push (If you have the code locally)

```bash
# Add all changes
git add .

# Commit the changes
git commit -m "Update patient limit to 500 and add Cloudinary for persistent media storage"

# Push to GitHub
git push origin main
```

Render will automatically redeploy when it detects the push.

## Step 5: Verify Everything Works

After deployment completes:

### Test Patient Limit
1. **Go to**: https://capstone-system-final.onrender.com/appointments/admin/patients/
2. **Verify**: Total Patients shows **500** (or close to 500)
3. **Check**: Patient IDs are sequential from low numbers (1, 2, 3, etc.)

### Test Image Upload
1. **Go to**: https://capstone-system-final.onrender.com/appointments/admin/manage-service-images/
2. **Upload a test image** for any service
3. **Verify**: Image appears immediately
4. **Redeploy** your app (Manual Deploy → Deploy latest commit)
5. **Check again**: The uploaded image should **still be there** ✅

Same test for product images:
- https://capstone-system-final.onrender.com/appointments/admin/manage-product-images/

## Expected Results

### Patient Management
- ✅ Total patients limited to **500**
- ✅ Patient IDs start from **1** and go up to **500**
- ✅ System performance improved with fewer patients

### Image Storage
- ✅ Service images stay after redeployment
- ✅ Product images stay after redeployment
- ✅ Profile pictures stay after redeployment
- ✅ All uploaded images are now **permanent** (indi na mawala)

## How It Works

### Before (Problem)
```
Upload Image → Render Server (Temporary) → ❌ Deleted on Redeploy
```

### After (Solution)
```
Upload Image → Cloudinary Cloud Storage → ✅ Permanent Storage
                     ↓
              Render displays from Cloudinary
```

## Cloudinary Free Tier Limits
- **Storage**: 25 GB (more than enough for a clinic)
- **Bandwidth**: 25 GB/month
- **Transformations**: 25,000/month
- **Cost**: $0 (completely free)

## Troubleshooting

### Images not uploading?
1. Check Render environment variables are set correctly
2. Verify Cloudinary credentials are correct
3. Check Render logs for errors: Dashboard → Logs

### Old images missing?
- This is **expected** - images uploaded before Cloudinary setup were on temporary storage
- **Solution**: Re-upload important images - they will now persist

### Still using local storage?
- Check `USE_CLOUDINARY=True` in Render environment variables
- Redeploy after adding environment variables

## Support

If you encounter any issues:
1. Check Render Logs for errors
2. Verify Cloudinary credentials
3. Ensure all environment variables are set
4. Try a fresh manual deploy

## Summary of Changes

### Files Modified
1. ✅ `accounts/management/commands/limit_patients.py` - Default limit changed to 500
2. ✅ `build.sh` - Deployment script updated to limit 500 patients
3. ✅ `requirements.txt` - Added Cloudinary packages
4. ✅ `beauty_clinic_django/settings.py` - Configured Cloudinary storage

### What to Do Next
1. ✅ Create Cloudinary account
2. ✅ Add environment variables on Render
3. ✅ Deploy the updated code
4. ✅ Test patient limit (should be 500)
5. ✅ Test image upload (should persist after redeploy)

---

**Note**: After completing these steps, all your uploaded images will be stored permanently on Cloudinary's cloud servers and will never be deleted, even after multiple redeployments! 🎉
