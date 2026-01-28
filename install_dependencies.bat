@echo off
:: Disable command echoing to keep the terminal output clean.

echo Installing required dependencies for the subtitle corpus search tool...
:: Notify the user that the dependency installation process has started.

pip install -r requirements.txt
:: Use the Python package manager to install all required libraries listed in requirements.txt.

echo.
:: Insert a blank line for readability.

echo Dependency installation completed successfully!
echo.

echo You can now run the program using:
echo python CorpusSearchTool.py
echo.

pause
:: Keep the terminal window open until a key is pressed.
