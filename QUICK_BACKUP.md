# Quick Database Backup Guide

## Fastest Way to Backup Your Render Database

### Step 1: Get Your Database URL

1. Go to https://dashboard.render.com/
2. Click on your database service (`beauty-clinic-db`)
3. Go to **"Info"** tab
4. Copy the **"External Database URL"** (looks like: `postgresql://user:pass@host:port/dbname`)

### Step 2: Run Backup

**Windows (Easiest):**
```powershell
# Set the DATABASE_URL
$env:DATABASE_URL="postgresql://user:pass@host:port/dbname"

# Run the backup script
python backup_remote_database.py
```

Or double-click `backup_database.bat` (after setting DATABASE_URL)

**Using Django Command:**
```powershell
# Set the DATABASE_URL
$env:DATABASE_URL="postgresql://user:pass@host:port/dbname"

# Run Django backup command
python manage.py backup_database --compress
```

**Direct pg_dump:**
```powershell
# Set password
$env:PGPASSWORD="your_password"

# Run pg_dump
pg_dump -h hostname -p 5432 -U username -d database_name -F c -f backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').dump
```

### Step 3: Find Your Backup

Backups are saved in the `backups/` folder:
- Format: `db_backup_YYYYMMDD_HHMMSS.sql` or `.sql.gz`
- Example: `backups/db_backup_20250120_143022.sql.gz`

---

## Troubleshooting

**"pg_dump not found"**
- Install PostgreSQL client: https://www.postgresql.org/download/windows/
- Or use the Python script which will guide you

**"Connection refused"**
- Make sure you're using the **External Database URL** (not Internal)
- Check that your IP is allowed (Render free tier may have restrictions)

**"Authentication failed"**
- Double-check your username and password in the DATABASE_URL

---

For detailed instructions, see `BACKUP_DATABASE_GUIDE.md`

