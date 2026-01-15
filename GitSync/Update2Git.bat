@echo off
:: Set code page to UTF-8 for proper character display
chcp 65001 >nul

REM Change to parent directory (project root)
cd /d "%~dp0.."

:: Step 1: Clean Python cache
echo [1/5] Cleaning Python cache folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: Step 2: Clean compiled files
echo [2/5] Cleaning compiled files...
del /s /q *.pyc *.pyo >nul 2>&1

:: Step 3: Gitignore check
echo [3/5] Checking Git ignore configuration...
if not exist ".gitignore" goto :git_ops
findstr /i "GitSync" ".gitignore" >nul
if errorlevel 1 goto :git_ops

echo WARNING: GitSync found in .gitignore, removing entry...
findstr /v /i "GitSync" ".gitignore" > ".gitignore.tmp"
move /y ".gitignore.tmp" ".gitignore" >nul

:git_ops
:: Step 4: Standard Git workflow
echo [4/5] Switching to main branch and adding changes...
git checkout main
git add -A

echo [5/5] Committing and Pushing changes...
set "msg=Daily update"
set /p msg="Enter message (Press Enter for 'Daily update'): "
git commit -m "%msg%"
git push origin main --force

:: Check if the push was successful
if errorlevel 1 goto :push_failed

:push_success
echo.
echo ========================================
echo [SUCCESS] Update completed and pushed!
echo ========================================
echo.
:: Step 6: Display Summary with Full Paths and Extensions
echo  STATUS          FILE NAME
echo --------------------------------------------------------------------------
:: tokens=1,* ensures the second variable %%b captures the FULL path even with spaces
for /f "tokens=1,*" %%a in ('git log -1 --name-status --format^=') do (
    if "%%a"=="M" echo  Modified    :  %%b
    if "%%a"=="A" echo  Added       :  %%b
    if "%%a"=="D" echo  Deleted     :  %%b
    if "%%a"=="R" echo  Renamed     :  %%b
)
echo --------------------------------------------------------------------------
goto :final_end

:push_failed
echo.
echo ========================================
echo [ERROR] Push failed. Check your network.
echo ========================================

:final_end
echo.
pause
exit /b 0