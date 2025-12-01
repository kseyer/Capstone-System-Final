@echo off
echo ========================================
echo   FIXING PYTHON 3.13 ERROR
echo ========================================
echo.

cd /d "%~dp0"
if not exist "manage.py" (
    echo [ERROR] Please run this from project root folder!
    pause
    exit /b 1
)

echo Step 1: Checking Python 3.11...
if exist "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe" (
    echo Python 3.11.9 found!
) else (
    echo [ERROR] Python 3.11 not found!
    echo Please install Python 3.11 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Step 2: Deleting old virtual environment...
if exist ".venv" (
    echo Deleting .venv folder...
    rd /s /q ".venv" 2>nul
    if exist ".venv" (
        echo [WARNING] Could not delete .venv - it may be in use.
        echo Please close PyCharm and any terminals, then run this script again.
        pause
        exit /b 1
    )
    echo .venv deleted successfully!
) else (
    echo No .venv folder found.
)

if exist "venv" (
    echo Deleting venv folder...
    rd /s /q "venv" 2>nul
    if exist "venv" (
        echo [WARNING] Could not delete venv - it may be in use.
        echo Please close PyCharm and any terminals, then run this script again.
        pause
        exit /b 1
    )
    echo venv deleted successfully!
)

echo.
echo Step 3: Creating new virtual environment with Python 3.11...
echo NOTE: If this fails, your project path may be too long.
echo Consider moving project to a shorter path like C:\Projects\beauty_clinic_django
"C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create virtual environment!
    echo.
    echo SOLUTION: Your project path is too long for Windows.
    echo Please move the project to a shorter path like:
    echo   C:\Projects\beauty_clinic_django
    echo Then run this script again.
    pause
    exit /b 1
)
echo Virtual environment created successfully!

echo.
echo Step 4: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 5: Verifying Python version...
python --version
echo.

echo Step 6: Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo Step 7: Installing dependencies...
echo This may take 2-5 minutes, please wait...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully!

echo.
echo Step 8: Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migration failed!
    pause
    exit /b 1
)
echo Migrations completed successfully!

echo.
echo Step 9: Creating admin user...
python create_admin.py
if errorlevel 1 (
    echo [WARNING] Could not create admin user. You can create it manually later.
)

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Next steps in PyCharm:
echo 1. File -^> Settings -^> Project -^> Python Interpreter
echo 2. Add Interpreter -^> Existing Environment
echo 3. Select: venv\Scripts\python.exe
echo 4. Create Django Server run configuration
echo 5. Run the server!
echo.
echo Admin login:
echo URL: http://127.0.0.1:8000/admin
echo Username: admin
echo Password: admin123
echo.
pause

