@echo off
echo Checking for Java...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Java is not installed. Please install Java JRE/JDK first.
    pause
    exit /b
)

echo Installing Python dependencies...
python -m pip install -r requirements.txt

echo Setup complete. Run 'python script.py [args]' to start.
pause