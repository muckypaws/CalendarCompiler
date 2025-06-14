@echo off
echo === CalendarCompiler Automated Installer (Windows) ===

REM Check for Python 3.8+
python --version 2>NUL | findstr /R "^Python 3\.[8-9]" >NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.8+ not found! Please install Python before continuing.
    pause
    exit /b 1
)

REM Check for git
where git >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Git not found! Please install git before continuing.
    pause
    exit /b 1
)

echo Cloning repository...
git clone https://github.com/muckypaws/CalendarCompiler.git
cd CalendarCompiler || exit /b 1

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Please install the cairo graphics library manually for Windows.
echo See: https://cairosvg.org/documentation/#installation
echo Or install MSYS2 (https://www.msys2.org/) and run: pacman -S mingw-w64-x86_64-cairo
echo.

echo Setup complete! Edit your config\settings.json and run:
echo   venv\Scripts\activate
echo   python CalendarCompiler.py
pause
