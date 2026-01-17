@echo off
REM Setup script for creating and activating a virtual environment

echo Creating virtual environment...
python -m venv venv

echo.
echo Virtual environment created successfully!
echo.
echo To activate the virtual environment, run:
echo     venv\Scripts\activate
echo.
echo Then install dependencies with:
echo     pip install -r requirements.txt
echo.
pause
