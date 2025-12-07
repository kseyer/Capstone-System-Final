# 🚀 Simple Steps to Run in PyCharm

## ⚠️ IMPORTANT: PyCharm Helper Error Fix

**If you see:** "Helper Exited with 1" error when creating venv in PyCharm

**Quick Fix:** Create the virtual environment manually using terminal (see `MANUAL_VENV_SETUP.md` for detailed steps)

**OR** try this in PyCharm Terminal:
1. Close PyCharm
2. Delete the `venv` folder manually (in File Explorer)
3. Reopen PyCharm
4. Open Terminal in PyCharm (`Alt+F12`)
5. Run: `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -m venv venv`
6. Then continue from Step 3 below

---

## ⚠️ IMPORTANT: Python 3.13 Error Fix

**If you see this error:** `ModuleNotFoundError: No module named 'appointments.migrations.0009...'`

**This is because Python 3.13 has compatibility issues with Django migrations.**

### Quick Fix - Switch to Python 3.11 or 3.12:

1. **Download Python 3.11 or 3.12** from https://www.python.org/downloads/
   - Choose Windows installer (64-bit)
   - **IMPORTANT:** Check "Add Python to PATH" during installation

2. **In PyCharm:**
   - **File → Settings** → **Project → Python Interpreter**
   - Click **gear icon** ⚙️ → **Add Interpreter → Add Local Interpreter**
   - Select **Virtualenv Environment** → **New Environment**
   - **Base Interpreter:** Browse and select Python 3.11 or 3.12 (usually in `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe` or similar)
   - **Location:** `venv` (in your project folder)
   - Click **OK**

3. **Delete old venv** (if it exists):
   - Close PyCharm
   - Delete the `venv` folder in your project
   - Reopen PyCharm

4. **Continue from Step 3 below** (Install Packages)

---

## Step 1: Open Project
1. Open **PyCharm**
2. Click **File → Open**
3. Select the **`beauty_clinic_django`** folder (the one with `manage.py` inside)
4. Click **OK**

## Step 2: Set Python Interpreter

**Option A: If you have Python 3.11 or 3.12 installed:**
1. Click **File → Settings** (or press `Ctrl+Alt+S`)
2. Go to **Project → Python Interpreter**
3. Click the **gear icon** ⚙️ → **Add Interpreter → Add Local Interpreter**
4. Select **Virtualenv Environment** → **New Environment**
5. **Base Interpreter:** Select Python 3.11 or 3.12 (NOT 3.13!)
6. **Location:** `venv` (in your project folder)
7. Click **OK**

**Option B: If venv already exists with Python 3.11/3.12:**
1. Click **File → Settings** (or press `Ctrl+Alt+S`)
2. Go to **Project → Python Interpreter**
3. Click the **gear icon** ⚙️ → **Add Interpreter → Add Local Interpreter**
4. Select **Virtualenv Environment** → **Existing Environment**
5. Browse to: `venv\Scripts\python.exe` (in your project folder)
6. **Verify:** Make sure it shows Python 3.11 or 3.12 (not 3.13!)
7. Click **OK**

## Step 3: Install Packages
1. Open **Terminal** in PyCharm (bottom toolbar, or press `Alt+F12`)
2. Type this command and press Enter:
   ```
   pip install -r requirements.txt
   ```
3. Wait for installation to complete (2-5 minutes)

## Step 4: Run Database Setup
In the same terminal, type:
```
python manage.py migrate
```
Press Enter and wait for it to finish.

## Step 5: Create Admin User (Optional)
If you need an admin account, run:
```
python create_admin.py
```
This creates:
- Username: `admin`
- Password: `admin123`

## Step 6: Create Run Configuration
1. Click **Run → Edit Configurations...**
2. Click the **+** button (top left)
3. Select **Django Server**
4. Set these values:
   - **Name**: `Django Server`
   - **Host**: `127.0.0.1`
   - **Port**: `8000`
   - **Working directory**: Click folder icon 📁 and select the `beauty_clinic_django` folder (where `manage.py` is)
5. Click **OK**

## Step 7: Run the Server
1. Select **Django Server** from the dropdown (top right)
2. Click the green **▶️ Run** button (or press `Shift+F10`)
3. Wait for: `Starting development server at http://127.0.0.1:8000/`
4. Open your browser and go to: **http://127.0.0.1:8000**

## ✅ Done!
Your application should now be running!

**Admin Panel:** http://127.0.0.1:8000/admin
- Username: `admin`
- Password: `admin123`

---

## ⚠️ If You Get Errors:

### Error: "ModuleNotFoundError" or Migration Errors
**Fix:** Use Python 3.11 or 3.12 instead of 3.13
1. Download Python 3.11 or 3.12 from python.org
2. In PyCharm, set interpreter to the new Python version
3. Delete `venv` folder
4. Create new venv with Python 3.11/3.12
5. Run `pip install -r requirements.txt` again

### Error: "manage.py not found"
**Fix:** Make sure Working Directory in run configuration points to the folder containing `manage.py`

### Error: "No module named 'django'"
**Fix:** Make sure you installed packages (Step 3) and selected the venv interpreter

### Port 8000 Already in Use
**Fix:** Change port to `8001` in the run configuration

