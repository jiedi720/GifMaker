
@echo off
chcp 65001 >nul
REM Change to parent directory (GitSync folder's parent)
cd /d "%~dp0.."
REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    pause
    exit /b 1
)
echo Git version check completed
REM Get current folder name as repo name (parent directory)
for %%i in (.) do set REPO_NAME=%%~ni
REM Construct GitHub URL based on folder name
REM Format: https://github.com/USERNAME/REPO_NAME.git
set "REPO_URL=https://github.com/jiedi720/%REPO_NAME%.git"
set "BRANCH=main"
echo ======================================
echo Force overwrite current folder with GitHub repo
echo Repo: %REPO_URL%
echo Branch: %BRANCH%
echo ======================================
echo.
echo WARNING: This will DISCARD all local changes!
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul
REM Initialize if not a git repo or if .git folder is empty/invalid
if not exist ".git" (
    echo Current directory is not a Git repo, initializing...
    git init
    git remote add origin %REPO_URL%
) else (
    REM Check if .git is a valid git repo by checking for HEAD file
    if not exist ".git\HEAD" (
        echo .git folder exists but is not a valid Git repo, reinitializing...
        rmdir /s /q ".git"
        git init
        git remote add origin %REPO_URL%
    )
)
echo Fetching remote repo...
echo [==========                    ] 25%% Fetching...
git fetch origin
if %errorlevel% neq 0 (
    echo ERROR: Failed to fetch from remote repository
    pause
    exit /b 1
)
echo Force overwriting local files...
echo [==================            ] 50%% Resetting...
git reset --hard origin/%BRANCH%
if %errorlevel% neq 0 (
    echo ERROR: Failed to reset to remote branch
    pause
    exit /b 1
)
echo Cleaning untracked files (including GitSync folder)...
echo [========================      ] 75%% Cleaning...
git clean -fd
echo [============================] 100%% Complete!
echo.
echo Overwrite completed successfully
echo Repository: %REPO_NAME%
pause
