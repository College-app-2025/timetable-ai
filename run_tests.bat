@echo off
echo 🚀 SIH TIMETABLE AI SYSTEM - TEST RUNNER
echo ========================================

echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo ✅ Python found! Running tests...
echo.

echo 📊 Creating sample database and preference tables...
python quick_test.py

echo.
echo 🎯 Test completed! Check the generated files:
echo    • sample_database.json
echo    • elective_preference_tables.json
echo    • SETUP_GUIDE.md

echo.
pause
