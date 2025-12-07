# 🔧 Manual Virtual Environment Setup (Fix PyCharm Helper Error)

If PyCharm's virtual environment helper is failing, create the venv manually using the terminal.

## Step 1: Close PyCharm
Close PyCharm completely to release any file locks on the venv folder.

## Step 2: Delete Old venv (if exists)
1. Open **File Explorer**
2. Navigate to your project: `beauty_clinic_django`
3. If you see a `venv` folder, **delete it** (right-click → Delete)
   - If it says "File is in use", close PyCharm and try again
   - Or restart your computer if needed

## Step 3: Open PowerShell or Command Prompt
1. Press `Win + R`
2. Type `powershell` and press Enter
3. Navigate to your project:
   ```powershell
   cd "C:\Users\User\Downloads\Skinovation_Clinic_V2-main BAG O NAMAN\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2-main\Skinovation_Clinic_V2\beauty_clinic_django"
   ```

## Step 4: Create Virtual Environment Manually
Run this command (use Python 3.11 or 3.12, NOT 3.13):

```powershell
C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

**OR if Python 3.11 is in your PATH:**
```powershell
python3.11 -m venv venv
```

**OR if you have Python 3.12:**
```powershell
C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
```

Wait for it to complete (should take 10-30 seconds).

## Step 5: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

You should see `(venv)` at the start of your prompt.

## Step 6: Verify Python Version
```powershell
python --version
```
Should show: `Python 3.11.x` or `Python 3.12.x` (NOT 3.13!)

## Step 7: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

## Step 8: Install Dependencies
```powershell
pip install -r requirements.txt
```
Wait for installation (2-5 minutes).

## Step 9: Run Migrations
```powershell
python manage.py migrate
```
This should work now! ✅

## Step 10: Create Admin User (Optional)
```powershell
python create_admin.py
```

## Step 11: Reopen PyCharm and Set Interpreter
1. **Open PyCharm**
2. **File → Settings** → **Project → Python Interpreter**
3. Click **gear icon** ⚙️ → **Add Interpreter → Add Local Interpreter**
4. Select **Virtualenv Environment** → **Existing Environment**
5. Browse to: `venv\Scripts\python.exe` (in your project folder)
6. Click **OK**

## Step 12: Create Run Configuration
1. **Run → Edit Configurations...**
2. Click **+** → **Django Server**
3. Set:
   - **Name:** `Django Server`
   - **Host:** `127.0.0.1`
   - **Port:** `8000`
   - **Working directory:** Click folder icon and select the `beauty_clinic_django` folder (where `manage.py` is)
4. Click **OK**

## Step 13: Run the Server
1. Select **Django Server** from dropdown (top right)
2. Click green **▶️ Run** button
3. Open http://127.0.0.1:8000

## ✅ Done!

Your application should now run without errors!

**Admin Panel:** http://127.0.0.1:8000/admin
- Username: `admin`
- Password: `admin123`

---

## Troubleshooting

### "Execution Policy" Error
If you get: `cannot be loaded because running scripts is disabled on this system`

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating venv again.

### "Python 3.11 not found"
**Fix:** Make sure Python 3.11 or 3.12 is installed:
1. Check: `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe`
2. Or download from: https://www.python.org/downloads/
3. During installation, check "Add Python to PATH"

### "Access Denied" when deleting venv
**Fix:**
1. Close PyCharm completely
2. Close any terminals using the venv
3. Restart your computer if needed
4. Then delete the venv folder

