# 🔧 Fix Python 3.13 Migration Error

## The Problem

You're seeing this error:
```
ModuleNotFoundError: No module named 'appointments.migrations.0009_feedback_attendant_rating_alter_feedback_rating'
```

**Why?** Python 3.13 cannot import modules that start with numbers. Django migration files like `0009_...py` start with numbers, causing this error.

## The Solution: Use Python 3.11 or 3.12

### Step-by-Step Fix in PyCharm:

#### Step 1: Download Python 3.11 or 3.12
1. Go to https://www.python.org/downloads/
2. Download **Python 3.11.9** or **Python 3.12.7** (Windows 64-bit installer)
3. Run the installer
4. **⚠️ CRITICAL:** Check the box **"Add Python to PATH"**
5. Click "Install Now"
6. Wait for installation to complete

#### Step 2: Delete Old Virtual Environment
1. Close PyCharm completely
2. Navigate to your project folder: `beauty_clinic_django`
3. Delete the `venv` folder (right-click → Delete)
4. Reopen PyCharm

#### Step 3: Create New Virtual Environment in PyCharm
1. **File → Settings** (or `Ctrl+Alt+S`)
2. Go to **Project → Python Interpreter**
3. Click the **gear icon** ⚙️ (next to interpreter dropdown)
4. Select **Add Interpreter → Add Local Interpreter**
5. Choose **Virtualenv Environment**
6. Select **New Environment**
7. **Base Interpreter:** 
   - Click the folder icon 📁
   - Navigate to: `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe` (or Python312)
   - OR click the dropdown and select Python 3.11 or 3.12 if it appears
8. **Location:** Should show `C:\...\beauty_clinic_django\venv`
9. Click **OK**

#### Step 4: Verify Python Version
1. In PyCharm, open **Terminal** (bottom toolbar, or `Alt+F12`)
2. Type: `python --version`
3. You should see: `Python 3.11.x` or `Python 3.12.x` (NOT 3.13!)

#### Step 5: Install Dependencies
In the PyCharm terminal, run:
```bash
pip install -r requirements.txt
```
Wait for installation to complete (2-5 minutes).

#### Step 6: Run Migrations
```bash
python manage.py migrate
```
This should now work without errors! ✅

#### Step 7: Create Admin User (Optional)
```bash
python create_admin.py
```

#### Step 8: Run the Server
1. **Run → Edit Configurations...**
2. Click **+** → **Django Server**
3. Set:
   - **Name:** `Django Server`
   - **Host:** `127.0.0.1`
   - **Port:** `8000`
   - **Working directory:** Click folder icon and select the `beauty_clinic_django` folder (where `manage.py` is)
4. Click **OK**
5. Click the green **▶️ Run** button
6. Open http://127.0.0.1:8000

## ✅ Success!

Your application should now run without errors!

**Admin Panel:** http://127.0.0.1:8000/admin
- Username: `admin`
- Password: `admin123`

---

## Alternative: If You Must Use Python 3.13

If you absolutely cannot use Python 3.11/3.12, you can try:

1. Update Django to the latest version (may have fixes):
   ```bash
   pip install --upgrade django
   ```

2. Or wait for Django to release a Python 3.13 compatible version.

**However, the recommended solution is to use Python 3.11 or 3.12.**

