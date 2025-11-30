@echo off
echo ========================================
echo   Skinovation Clinic - Setup Script
echo ========================================
echo.

REM Navigate to the correct directory (where manage.py and requirements.txt are)
cd /d "%~dp0"
if not exist "manage.py" (
    echo [ERROR] manage.py not found!
    echo Please make sure you're running this script from the project root folder.
    echo The folder should contain: manage.py, requirements.txt, and setup.bat
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version
echo.

echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

echo [3/6] Activating virtual environment and upgrading pip...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
)
python -m pip install --upgrade pip
echo.

echo [4/6] Installing required packages...
echo This may take a few minutes, please wait...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install packages!
    pause
    exit /b 1
)
echo Packages installed successfully!
echo.

echo [5/6] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migration failed!
    pause
    exit /b 1
)
echo Database setup complete!
echo.

echo [6/6] Setting up admin user...
python manage.py shell -c "from accounts.models import User; exists = User.objects.filter(username='admin').exists(); exit(0 if exists else 1)" >nul 2>&1
if errorlevel 1 (
    echo Creating default admin user...
    python create_admin.py
    if errorlevel 1 (
        echo [WARNING] Could not create admin user automatically.
        echo You can create one manually later using: python manage.py createsuperuser
    )
) else (
    echo Admin user already exists. Skipping...
    echo.
    echo If you need to reset admin password, run: python create_admin.py
)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the server, run: run.bat
echo Or manually run: python manage.py runserver
echo.
echo Then open your browser to: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin
echo.
pause

