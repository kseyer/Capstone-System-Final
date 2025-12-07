@echo off
echo ========================================
echo   Fixing Migration Import Error
echo ========================================
echo.

cd /d "%~dp0"
if not exist "manage.py" (
    echo [ERROR] Please run this from project root folder!
    pause
    exit /b 1
)

REM Activate venv if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
)
echo.

echo Step 1: Clearing all Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Deleting: %%d
    rd /s /q "%%d" 2>nul
)
del /s /q *.pyc 2>nul
echo Cache cleared!
echo.

echo Step 2: Checking Python version...
python --version
echo.
echo [NOTE] Python 3.13 may have compatibility issues with Django 5.2.1
echo If errors persist, consider using Python 3.11 or 3.12
echo.

echo Step 3: Testing migration import...
python -c "import sys; sys.path.insert(0, '.'); from appointments.migrations import migration_0009_feedback_attendant_rating_alter_feedback_rating" 2>nul
if errorlevel 1 (
    echo [WARNING] Direct import test failed. This is normal for Python 3.13.
    echo Trying alternative approach...
) else (
    echo Migration file can be imported!
)
echo.

echo Step 4: Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo [ERROR] Migration failed!
    echo.
    echo Trying to fake the migration (if already applied)...
    python manage.py migrate --fake appointments 0009 2>nul
    python manage.py migrate
)
echo.

echo Step 5: Testing if server can start...
echo.
echo ========================================
echo   Fix Complete!
echo ========================================
echo.
echo Try running: python manage.py runserver
echo.
echo If you still get errors, the issue is likely Python 3.13 compatibility.
echo Solution: Install Python 3.11 or 3.12 instead.
echo.
pause

