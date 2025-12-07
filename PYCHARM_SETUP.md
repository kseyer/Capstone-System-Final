# 🚀 PyCharm Setup Guide

Follow these steps to run the project in PyCharm.

## Step 1: Open Project in PyCharm

1. **Open PyCharm**
2. **File → Open** (or **File → Open Folder**)
3. Navigate to and select the **`beauty_clinic_django`** folder
   - This is the folder that contains `manage.py`, `requirements.txt`, and `setup.bat`
4. Click **OK**

## Step 2: Set Up Python Interpreter

### Option A: Use Existing Virtual Environment (Recommended)

If you already ran `setup.bat`, you should have a `venv` folder:

1. **File → Settings** (or press `Ctrl+Alt+S`)
2. Go to **Project → Python Interpreter**
3. Click the gear icon ⚙️ next to the interpreter dropdown
4. Select **Add Interpreter → Add Local Interpreter**
5. Choose **Virtualenv Environment**
6. Select **Existing Environment**
7. Click the folder icon 📁 and browse to: `venv\Scripts\python.exe`
   - Full path should be: `C:\...\beauty_clinic_django\venv\Scripts\python.exe`
8. Click **OK**

### Option B: Create New Virtual Environment

If you don't have a `venv` folder yet:

1. **File → Settings** → **Project → Python Interpreter**
2. Click the gear icon ⚙️ → **Add Interpreter → Add Local Interpreter**
3. Select **Virtualenv Environment** → **New Environment**
4. **Location**: Should be `C:\...\beauty_clinic_django\venv`
5. **Base Interpreter**: 
   - ⚠️ **IMPORTANT**: Select Python 3.11 or 3.12 (NOT 3.13!)
   - If you only have Python 3.13, download Python 3.11 or 3.12 from python.org
6. Check **"Inherit global site-packages"** (optional)
7. Click **OK**

## Step 3: Install Dependencies

1. Open the **Terminal** in PyCharm (bottom toolbar, or **Alt+F12**)
2. Make sure you're in the project root (where `manage.py` is)
3. If you created a new venv, activate it:
   ```bash
   venv\Scripts\activate
   ```
4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Run Database Migrations

In the PyCharm terminal:

```bash
python manage.py migrate
```

## Step 5: Create Run Configuration

### Method 1: Using PyCharm's Django Support (Easiest)

1. **Run → Edit Configurations...**
2. Click the **+** button (top left)
3. Select **Django Server**
4. Configure:
   - **Name**: `Django Server` (or any name you like)
   - **Host**: `127.0.0.1`
   - **Port**: `8000`
   - **Python interpreter**: Select your venv interpreter (Python 3.11 or 3.12)
   - **Working directory**: Should be the project root (where `manage.py` is)
     - Click folder icon 📁 and select the `beauty_clinic_django` folder
   - **Environment variables**: Leave empty (or add if needed)
5. Click **OK**

### Method 2: Using manage.py (Alternative)

1. **Run → Edit Configurations...**
2. Click **+** → Select **Python**
3. Configure:
   - **Name**: `Run Server`
   - **Script path**: Click folder icon and select `manage.py`
   - **Parameters**: `runserver`
   - **Working directory**: Project root folder
   - **Python interpreter**: Your venv interpreter
4. Click **OK**

## Step 6: Run the Server

1. Select your run configuration from the dropdown (top right)
2. Click the green **▶️ Run** button (or press `Shift+F10`)
3. Wait for the server to start
4. You should see: `Starting development server at http://127.0.0.1:8000/`
5. Open your browser and go to: **http://127.0.0.1:8000**

## Step 7: Create Admin User (If Needed)

If you need to create an admin user:

1. Open PyCharm terminal
2. Run:
   ```bash
   python create_admin.py
   ```
   Or:
   ```bash
   python manage.py createsuperuser
   ```

**Default Admin Credentials:**
- URL: http://127.0.0.1:8000/admin
- Username: `admin`
- Password: `admin123`

## ⚠️ Important Notes

### Python Version Issue

**If you're using Python 3.13**, you may encounter migration import errors. 

**Solution:**
1. Download Python 3.11 or 3.12 from https://www.python.org/downloads/
2. Install it (check "Add Python to PATH")
3. In PyCharm, set the interpreter to Python 3.11 or 3.12
4. Delete the `venv` folder
5. Create a new virtual environment with Python 3.11/3.12
6. Run `pip install -r requirements.txt` again

### Working Directory

Make sure your **Working Directory** in the run configuration points to:
- The folder containing `manage.py`
- NOT the inner `beauty_clinic_django` folder
- NOT any subfolder

**Correct path example:**
```
C:\Users\User\...\beauty_clinic_django
```

**Wrong paths:**
```
C:\Users\User\...\beauty_clinic_django\beauty_clinic_django  ❌
C:\Users\User\...\beauty_clinic_django\accounts  ❌
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'appointments.migrations.0009...'"

**Cause**: Python 3.13 compatibility issue

**Fix**: 
1. Use Python 3.11 or 3.12 instead
2. Or run `fix_migration.bat` from command prompt

### Error: "manage.py not found"

**Cause**: Wrong working directory

**Fix**: 
1. In run configuration, set Working Directory to project root
2. Make sure it's the folder containing `manage.py`

### Error: "No module named 'django'"

**Cause**: Virtual environment not activated or packages not installed

**Fix**:
1. Make sure you selected the venv interpreter in PyCharm
2. In terminal, run: `pip install -r requirements.txt`

### Server won't start

**Fix**:
1. Check if port 8000 is already in use
2. Change port in run configuration to 8001
3. Or close the other program using port 8000

## Quick Checklist

- [ ] Project opened in PyCharm
- [ ] Python interpreter set to venv (Python 3.11 or 3.12)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Run configuration created (Django Server)
- [ ] Working directory set correctly
- [ ] Server starts successfully
- [ ] Can access http://127.0.0.1:8000 in browser

---

**That's it! Your project should now run in PyCharm.** 🎉



