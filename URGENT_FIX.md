# 🚨 URGENT: Fix Python 3.13 Error - Simple Solution

## The Problem
You're getting: `ModuleNotFoundError: No module named 'appointments.migrations.0009...'`

**This is because you're using Python 3.13, which cannot import Django migration files.**

## ⚡ QUICK FIX (Choose One):

### Option 1: Use the Fix Script (Easiest)

1. **Close PyCharm completely** (important!)
2. **Double-click** `fix_python313.bat` in File Explorer
3. Wait 2-5 minutes for it to complete
4. **Reopen PyCharm** and set interpreter to `venv\Scripts\python.exe`
5. **Done!** ✅

---

### Option 2: Move Project to Shorter Path (If Option 1 Fails)

Your project path is very long, which can cause issues on Windows.

1. **Close PyCharm**
2. **Move the project** to a shorter path:
   - From: `C:\Users\User\Downloads\Skinovation_Clinic_V2-main BAG O NAMAN\...\beauty_clinic_django`
   - To: `C:\Projects\beauty_clinic_django`
3. **Open PyCharm** → Open the moved project
4. **Run** `fix_python313.bat` in the new location
5. **Done!** ✅

---

### Option 3: Manual Fix in PyCharm Terminal

1. **Close PyCharm**
2. **Delete** `.venv` and `venv` folders manually (in File Explorer)
3. **Reopen PyCharm**
4. **Open Terminal** in PyCharm (`Alt+F12`)
5. **Run these commands:**

```powershell
# Create venv with Python 3.11
C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install packages
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin
python create_admin.py
```

6. **Set interpreter** in PyCharm: `venv\Scripts\python.exe`
7. **Create Django Server** run configuration
8. **Run!** ✅

---

## After Fix: Set Up PyCharm

1. **File → Settings → Project → Python Interpreter**
2. **Add Interpreter → Existing Environment**
3. Select: `venv\Scripts\python.exe`
4. **Run → Edit Configurations**
5. **Add → Django Server**
   - Host: `127.0.0.1`
   - Port: `8000`
   - Working directory: Select folder with `manage.py`
6. **Run!**

---

## ✅ Success!

Your app should now run at: **http://127.0.0.1:8000**

**Admin:** http://127.0.0.1:8000/admin
- Username: `admin`
- Password: `admin123`

---

## Still Having Issues?

The most common problem is the **long project path**. Windows has a 260-character path limit.

**Best solution:** Move project to `C:\Projects\beauty_clinic_django` and try again.

