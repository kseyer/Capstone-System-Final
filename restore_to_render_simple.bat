@echo off
REM Simple Database Restore to Render - No Shell Needed!
REM This restores your local backup directly to Render's database

echo ============================================================
echo Restore Database to Render.com
echo ============================================================
echo.

REM Set your Render database URL
set DATABASE_URL=postgresql://beauty_clinic_user:ddFysAOCJzUunwErwH24lzwA7OoI82st@dpg-d4lu336uk2gs738k18ug-a.oregon-postgres.render.com/beauty_clinic

REM Use the most recent backup file
set BACKUP_FILE=backups\db_backup_20251201_014313.json

echo Target: Render.com Production Database
echo Backup: %BACKUP_FILE%
echo.
echo ============================================================
echo WARNING: This will OVERWRITE all data in Render database!
echo ============================================================
echo.
set /p confirm="Are you sure? Type 'yes' to continue: "

if /i not "%confirm%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Connecting to Render database...
echo Restoring data... This may take a few minutes...
echo.

REM Restore the database
python manage.py loaddata %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo ✓ SUCCESS! Database restored to Render!
    echo ============================================================
    echo.
    echo Your data is now live at: https://capstone-system-final.onrender.com/
    echo.
) else (
    echo.
    echo ============================================================
    echo ✗ Restore failed!
    echo ============================================================
    echo.
    echo Common issues:
    echo 1. Check your internet connection
    echo 2. Verify DATABASE_URL is correct
    echo 3. Make sure backup file exists: %BACKUP_FILE%
    echo 4. Try running migrations first: python manage.py migrate
    echo.
)

pause

