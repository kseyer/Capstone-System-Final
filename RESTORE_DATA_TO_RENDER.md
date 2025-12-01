# 🔄 Restore Your Data to Render - Complete Guide

Your data is safe in the backup file! Follow these steps to restore it to your hosted Render system.

## 📋 What You Have

- **Backup File**: `backups/db_backup_20251120_024926.sqlite3` (704 KB)
- **Hosted System**: https://capstone-system-final.onrender.com/
- **Database URL**: Already configured in `restore_to_render_simple.bat`

## 🚀 Option 1: Quick Restore (Recommended)

### Step 1: Restore Backup Locally & Export to JSON

Run these commands one by one:

```bash
# 1. Copy the backup to use as your local database
copy backups\db_backup_20251120_024926.sqlite3 db.sqlite3

# 2. Run migrations to ensure schema is up to date
python manage.py migrate

# 3. Export data to JSON format (compatible with PostgreSQL on Render)
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -o backups/db_backup_for_render.json --exclude contenttypes --exclude auth.permission --exclude sessions.session --exclude admin.logentry
```

### Step 2: Upload Data to Render via Shell

1. Go to your Render Dashboard: https://dashboard.render.com/
2. Click on your web service: **capstone-system-final**
3. Click the **"Shell"** tab at the top
4. In the Render shell, run:

```bash
# Download the backup file from your GitHub repository
curl -o db_backup.json https://raw.githubusercontent.com/kseyer/Capstone-System-Final/main/backups/db_backup_for_render.json

# Load the data into Render's PostgreSQL database
python manage.py loaddata db_backup.json
```

### Step 3: Verify Data Restoration

Visit your Render website and log in with your original credentials!

---

## 🔧 Option 2: Direct Database Restore (Alternative Method)

If you want to restore directly from your local machine:

### Step 1: Push Backup to GitHub

```bash
# Add the JSON backup file to git
git add backups/db_backup_for_render.json
git commit -m "Add database backup for Render restoration"
git push origin main
```

### Step 2: Use Render Shell

Follow the same shell commands from Option 1, Step 2.

---

## 🛠️ Option 3: Using the Restoration Script

You have a restoration script, but it needs the backup in JSON format first.

### Step 1: Convert SQLite Backup to JSON

```bash
# Copy backup as current database
copy backups\db_backup_20251120_024926.sqlite3 db.sqlite3

# Migrate
python manage.py migrate

# Export to JSON
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -o backups/db_backup_for_render.json --exclude contenttypes --exclude auth.permission --exclude sessions.session
```

### Step 2: Update the Restoration Script

Edit `restore_to_render_simple.bat` line 14:

```batch
set BACKUP_FILE=backups\db_backup_for_render.json
```

### Step 3: Set the DATABASE_URL

Make sure the DATABASE_URL in the script matches your Render database. 

**⚠️ IMPORTANT**: Get your current DATABASE_URL from Render:
1. Go to Render Dashboard → Your Database
2. Copy the **Internal Database URL**
3. Update line 11 in `restore_to_render_simple.bat`

### Step 4: Run the Script

```bash
restore_to_render_simple.bat
```

Type `yes` when prompted to confirm.

---

## 📝 Important Notes

### About Database Backups:

- **SQLite backup** (`.sqlite3`): Your local database backup - contains all data
- **JSON backup** (`.json`): Portable format that works with any database (SQLite, PostgreSQL, MySQL)

### Data That Will Be Restored:

✅ All users (patients, attendants, admin, owner)  
✅ All services and packages  
✅ All products  
✅ All appointments  
✅ All feedback and notifications  
✅ All analytics data  
✅ All closed days and schedules  

### Troubleshooting:

**If restoration fails in Render Shell:**

1. First, flush the database:
   ```bash
   python manage.py flush --no-input
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Then try loading data again:
   ```bash
   python manage.py loaddata db_backup.json
   ```

**If you get "File not found" error:**

- Make sure you pushed the JSON file to GitHub first
- Check the URL is correct (GitHub raw content URL)
- Or upload the file manually (see Option 4 below)

---

## 📤 Option 4: Manual File Upload (If Above Methods Don't Work)

If the shell method doesn't work, you can:

1. **Install PostgreSQL client** on your local machine
2. **Connect directly** to Render's PostgreSQL database using the External Database URL
3. **Run the restoration script** from your local machine

This requires the `psycopg2` library and direct database access.

---

## 🎯 Recommended Approach

**I recommend Option 1** because:
- ✅ Simple and straightforward
- ✅ Uses Render's built-in shell (no additional tools needed)
- ✅ Direct access to production environment
- ✅ Can verify immediately after restoration

---

## ⚡ Quick Commands Summary

```bash
# Step 1: Prepare data locally
copy backups\db_backup_20251120_024926.sqlite3 db.sqlite3
python manage.py migrate
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -o backups/db_backup_for_render.json --exclude contenttypes --exclude auth.permission --exclude sessions.session

# Step 2: Push to GitHub
git add backups/db_backup_for_render.json
git commit -m "Add database backup for restoration"
git push origin main

# Step 3: In Render Shell (https://dashboard.render.com)
curl -o db_backup.json https://raw.githubusercontent.com/kseyer/Capstone-System-Final/main/backups/db_backup_for_render.json
python manage.py loaddata db_backup.json
```

---

## ✅ After Restoration

1. Visit your site: https://capstone-system-final.onrender.com/
2. Log in with your original credentials
3. Verify all data is present
4. Check:
   - Users can log in
   - Services are displayed
   - Appointments are showing
   - Admin panel has all data

---

**Need help?** Let me know if you encounter any errors during the restoration process!
