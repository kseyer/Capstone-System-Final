# Quick Restore - No Shell Needed! 🚀

Since Render Shell requires payment, here's how to restore your database **directly from your computer**:

## ⚡ Fastest Method (One Click!)

**Just double-click:** `restore_to_render_simple.bat`

That's it! It will restore your database to Render.

---

## 📝 Manual Method (Copy-Paste)

Open PowerShell and run these commands:

```powershell
# Set Render database URL
$env:DATABASE_URL="postgresql://beauty_clinic_user:ddFysAOCJzUunwErwH24lzwA7OoI82st@dpg-d4lu336uk2gs738k18ug-a.oregon-postgres.render.com/beauty_clinic"

# Restore your backup
python manage.py loaddata backups\db_backup_20251201_014313.json
```

---

## ✅ What This Does

1. Connects to your Render database (using the external URL)
2. Loads all data from your backup file
3. Overwrites existing data in Render
4. Your website will have the restored data!

---

## ⚠️ Important

- **This will DELETE all current data** in Render and replace it with your backup
- Make sure `db_backup_20251201_014313.json` is the backup you want to use
- The restore may take 2-5 minutes depending on data size

---

## 🔍 Verify It Worked

After running, check your website:
https://capstone-system-final.onrender.com/

You should see your restored data!

---

## 🆘 Troubleshooting

**"Connection refused"**
- Check your internet connection
- Make sure you're using the External Database URL (not Internal)

**"Table doesn't exist"**
- Run migrations first:
  ```powershell
  $env:DATABASE_URL="your_url_here"
  python manage.py migrate
  python manage.py loaddata backups\db_backup_20251201_014313.json
  ```

**"File not found"**
- Make sure the backup file exists: `backups\db_backup_20251201_014313.json`

---

That's all you need! No shell access required! 🎉

