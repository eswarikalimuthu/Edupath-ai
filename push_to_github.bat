@echo off
echo ==============================================
echo Pushing EduPath AI to GitHub: eswarikalimuthu
echo ==============================================

"d:\Edupath ai\tools\git\cmd\git.exe" remote -v
"d:\Edupath ai\tools\git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Pushed to https://github.com/eswarikalimuthu/Edupath-ai
) else (
    echo.
    echo [NOTE] If push failed:
    echo 1. Make sure you created the repository at https://github.com/new with name: Edupath-ai
    echo 2. If using a GitHub Token, run:
    echo    "d:\Edupath ai\tools\git\cmd\git.exe" remote set-url origin https://YOUR_TOKEN@github.com/eswarikalimuthu/Edupath-ai.git
    echo    "d:\Edupath ai\tools\git\cmd\git.exe" push -u origin main
)
pause
