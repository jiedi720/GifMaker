@echo off
chcp 65001 >nul

echo ============================================
echo Clear Parent Folder Script (Move to Recycle Bin)
echo ============================================
echo.
echo This will MOVE all files and folders in the parent directory to Recycle Bin
echo EXCEPT:
echo   - .git folder (Git repository)
echo   - GitSync folder (This script's location)
echo.
echo WARNING: Files will be moved to Recycle Bin, not permanently deleted!
echo.
echo Current parent directory:
set "PARENT_DIR=%~dp0.."
cd /d "%PARENT_DIR%"
cd
echo.
echo Files and folders to be moved to Recycle Bin (excluded: .git, GitSync):
echo.
dir /b /a-d
dir /b /ad | findstr /v /i "^\.git$" | findstr /v /i "^GitSync$"
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul

echo.
echo Starting cleanup...
echo.

REM Change to parent directory
cd /d "%PARENT_DIR%"

REM Delete files and folders using PowerShell
set "PS_SCRIPT=%TEMP%\DeleteWithRecycle_%RANDOM%.ps1"

REM Create PowerShell script
(
echo $ErrorActionPreference = 'SilentlyContinue'
echo Add-Type -AssemblyName Microsoft.VisualBasic
echo.
) > "%PS_SCRIPT%"

REM Delete files directly
for /f "delims=" %%f in ('dir /b /a-d 2^>nul ^| findstr /v /i "^GitSync"') do (
    echo Moving file to Recycle Bin: %%f
    echo $filePath = Join-Path "%PARENT_DIR%" "%%f" >> "%PS_SCRIPT%"
    echo if ^(Test-Path $filePath^) { >> "%PS_SCRIPT%"
    echo     Write-Host "Moving to Recycle Bin: %%f" >> "%PS_SCRIPT%"
    echo     [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile^($filePath, 'OnlyErrorDialogs', 'SendToRecycleBin'^) >> "%PS_SCRIPT%"
    echo } >> "%PS_SCRIPT%"
)

REM Delete folders directly
for /f "delims=" %%d in ('dir /b /ad 2^>nul ^| findstr /v /i "^\.git$" ^| findstr /v /i "^GitSync$"') do (
    echo Moving folder to Recycle Bin: %%d
    echo $folderPath = Join-Path "%PARENT_DIR%" "%%d" >> "%PS_SCRIPT%"
    echo if ^(Test-Path $folderPath^) { >> "%PS_SCRIPT%"
    echo     Write-Host "Moving to Recycle Bin: %%d" >> "%PS_SCRIPT%"
    echo     [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory^($folderPath, 'OnlyErrorDialogs', 'SendToRecycleBin'^) >> "%PS_SCRIPT%"
    echo } >> "%PS_SCRIPT%"
)

REM Execute the PowerShell script
echo [========================      ] 75%% Moving to Recycle Bin...
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

REM Clean up PowerShell script
if exist "%PS_SCRIPT%" del /f /q "%PS_SCRIPT%"

echo [============================] 100%% Complete!

echo.
echo ============================================
echo Cleanup completed!
echo ============================================
echo.
echo All files and folders have been moved to Recycle Bin.
echo You can restore them from Recycle Bin if needed.
echo.
echo Remaining folders:
dir /b /ad
echo.
echo Remaining files:
dir /b /a-d 2>nul
if errorlevel 1 (
    echo (No files remaining)
)
echo.
pause