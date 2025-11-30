# 🔄 Restore Data to Render (FREE TIER) - No Shell Access Needed!

Since you're using Render's **free tier** (no Shell access), here are **3 alternative methods** to restore your data.

---

## ✅ **Method 1: Automatic Restoration on Next Deploy** (EASIEST - RECOMMENDED)

Your backup will automatically load when Render redeploys your app!

### What I've Already Done:
- ✅ Created the backup file: `backups/db_backup_for_render.json`
- ✅ Created a management command: `load_backup_data`
- ✅ Updated `build.sh` to automatically load backup on deployment

### What You Need to Do:

**Step 1: Push the changes to GitHub**

```bash
git add .
git commit -m "Add automatic data restoration for Render deployment"
git push origin main
```

**Step 2: Trigger Render Deployment**

Go to your Render Dashboard:
1. Visit: https://dashboard.render.com/
2. Click on **capstone-system-final**
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

**Step 3: Wait for Deployment**

Render will:
1. Install dependencies
2. Run migrations
3. **Automatically load your backup data** (this is new!)
4. Start the application

**Step 4: Verify**

Visit https://capstone-system-final.onrender.com/ and log in with your original credentials!

---

## 🔧 **Method 2: Using a One-Time Deployment Script**

Create a special deployment that loads data once.

### Step 1: Create a One-Time Load Flag

Add this environment variable in Render:

1. Go to Render Dashboard → Your Service → **Environment**
2. Add: `LOAD_BACKUP_DATA=true`
3. Save Changes (this will trigger a redeploy)

### Step 2: Update build.sh

I can update the build script to check for this flag and load data only once.

---

## 📡 **Method 3: Using Render's PostgreSQL External Connection**

If you want more control, you can connect directly to Render's database from your local machine.

### Requirements:
- PostgreSQL client (`psql`) or a GUI tool like pgAdmin
- Your Render database credentials

### Steps:

**Step 1: Get Database Credentials**

1. Go to Render Dashboard → Your PostgreSQL Database
2. Copy the **External Database URL** (looks like: `postgresql://user:password@host/database`)

**Step 2: Set Environment Variable Locally**

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://beauty_clinic_user:your_password@dpg-xxxxx.oregon-postgres.render.com/beauty_clinic"

# Or create a .env file with:
DATABASE_URL=postgresql://beauty_clinic_user:your_password@dpg-xxxxx.oregon-postgres.render.com/beauty_clinic
```

**Step 3: Load Data from Your Local Machine**

```bash
# This will load data directly to Render's database
python manage.py load_backup_data --backup-file backups/db_backup_for_render.json
```

---

## 🚀 **Method 4: API-Based Data Import** (Advanced)

Create a secure endpoint that imports data via HTTP request.

### Step 1: Create Import View

I can create a Django view protected by a secret token that loads the backup when accessed.

### Step 2: Access the URL

Visit: `https://capstone-system-final.onrender.com/admin/import-data/?token=YOUR_SECRET_TOKEN`

Would you like me to implement this method?

---

## 📋 **What's Included in Your Backup**

Your `db_backup_for_render.json` (197 KB) contains:

✅ All users (patients, attendants, admin, owner)  
✅ All services and service images  
✅ All products and product images  
✅ All packages  
✅ All appointments and bookings  
✅ All feedback and ratings  
✅ All notifications  
✅ All closed days and schedules  
✅ All store hours  
✅ All analytics data  

---

## ⚡ **RECOMMENDED: Use Method 1** (Automatic)

**Why?**
- ✅ Simplest - just push and redeploy
- ✅ No manual commands needed
- ✅ Works with free tier
- ✅ Automatic on every fresh deployment
- ✅ Already configured and ready to go!

---

## 📝 **Quick Commands for Method 1**

```bash
# 1. Push changes to GitHub
git add .
git commit -m "Enable automatic data restoration on Render"
git push origin main

# 2. Go to Render Dashboard and click "Manual Deploy"
# 3. Wait for deployment to complete
# 4. Visit your site and verify data is restored!
```

---

## 🛠️ **Troubleshooting**

### "Data not showing after deployment"

Check Render deployment logs:
1. Go to Render Dashboard → Your Service → **Logs**
2. Look for: `"JSON backup file found. Restoring from backup..."`
3. Check if there are any errors during restoration

### "IntegrityError" or "Duplicate key" in logs

The database might already have some data. Options:

**Option A**: Clear database before next deploy
- Add environment variable: `FLUSH_DB_BEFORE_RESTORE=true`
- Redeploy

**Option B**: Delete and recreate the PostgreSQL database
- Go to Render Dashboard → Database → Settings → Delete
- Create a new database
- Redeploy your service

### "Backup file not found" in logs

Make sure you pushed the backup file:
```bash
git add -f backups/db_backup_for_render.json
git commit -m "Add backup data file"
git push origin main
```

---

## 🎯 **Next Steps**

1. **Push the changes** (I've already created the files)
2. **Trigger a manual deploy** on Render
3. **Check the logs** to confirm restoration
4. **Visit your site** and verify data is back!

The easiest path is **Method 1** - everything is already set up! Just push and deploy. 🚀

---

**Need help with any of these methods?** Let me know which one you'd like to try!
