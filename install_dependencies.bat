@echo off
:: Simple dependency installation script

echo Installing dependencies...

:: Upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
python -m pip install -r requirements.txt

:: Check installation result
if %errorlevel% == 0 (
    echo.
    echo Dependencies installed successfully!
    echo.
    echo You can run your Python scripts using:
    echo python script_name.py
) else (
    echo.
    echo Dependency installation failed, please check error messages.
)

echo Press any key to continue...
pause >nul
