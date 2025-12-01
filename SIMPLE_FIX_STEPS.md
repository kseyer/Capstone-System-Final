# 🚨 URGENT FIX - Python 3.13 Error

## The Problem
You're using Python 3.13 which **cannot** import Django migration files. This is why you keep getting errors.

## The Solution (3 Simple Steps)

### Step 1: Close PyCharm
**IMPORTANT:** Close PyCharm completely to unlock files.

### Step 2: Run the Fix Script
1. Open **File Explorer**
2. Navigate to: `beauty_clinic_django` folder
3. **Double-click** `fix_python313.bat`
4. Wait for it to complete (2-5 minutes)
5. It will:
   - Delete old Python 3.13 venv
   - Create new Python 3.11 venv
   - Install all packages
   - Run migrations
   - Create admin user

### Step 3: Reopen PyCharm and Set Interpreter
1. **Open PyCharm**
2. **File → Settings** → **Project → Python Interpreter**
3. Click **gear icon** ⚙️ → **Add Interpreter → Add Local Interpreter**
4. Select **Virtualenv Environment** → **Existing Environment**
5. Browse to: `venv\Scripts\python.exe`
6. Click **OK**

### Step 4: Create Run Configuration
1. **Run → Edit Configurations...**
2. Click **+** → **Django Server**
3. Set:
   - **Name:** `Django Server`
   - **Host:** `127.0.0.1`
   - **Port:** `8000`
   - **Working directory:** Click folder icon → Select `beauty_clinic_django` folder (where `manage.py` is)
4. Click **OK**

### Step 5: Run!
1. Select **Django Server** from dropdown
2. Click green **▶️ Run** button
3. Open http://127.0.0.1:8000

## ✅ Done! No more errors!

---

## If the Script Fails

If `fix_python313.bat` says files are locked:

1. **Close PyCharm completely**
2. **Close all terminal windows**
3. **Restart your computer** (if needed)
4. **Run the script again**

---

## Manual Fix (If Script Doesn't Work)

Open **PowerShell** and run these commands one by one:

```powershell
cd "C:\Users\User\Downloads\Skinovation_Clinic_V2-main BAG O NAMAN\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2\beauty_clinic_django"

# Delete old venv
Remove-Item -Recurse -Force ".venv" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue

# Create new venv with Python 3.11
C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin
python create_admin.py
```

Then continue from Step 3 above.

