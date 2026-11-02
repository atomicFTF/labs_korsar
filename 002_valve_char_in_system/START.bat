@echo off
color 0A
title KORSAR + PROC Automatic Run
echo ====================================================
echo   STARTING KORSAR CALCULATION
echo ====================================================

set source_dir=task
set final_dir=result
set korpath=%~dp0..\korsar.exe

if not exist "%source_dir%\kordat" (
    echo ERROR: File %source_dir%\kordat not found!
    pause
    exit
)

if not exist "%korpath%" (
    echo ERROR: korsar.exe not found in %~dp0..
    pause
    exit
)

echo Cleaning results folder...
if exist "%final_dir%" (
    rd /q /s "%final_dir%"
)
md "%final_dir%"

echo Copying files...
copy "%source_dir%\kordat" "%final_dir%" >nul
copy "%~dp0..\nwsp_dat" "%final_dir%" >nul

echo.
echo ====================================================
echo   RUNNING KORSAR (Please wait, window will close)
echo ====================================================
cd "%final_dir%"
start /BELOWNORMAL /WAIT cmd /c ""%korpath%" > log_calc.txt"
cd ..

echo.
echo ====================================================
echo   CHECKING RESULTS
echo ====================================================

rem --- ИСПРАВЛЕНО: теперь проверяем korres (две буквы "р") ---
if exist "%final_dir%\korres" (
    echo [SUCCESS] Calculation finished. korres file created.
    echo Running PROC.bat...
    
    call PROC.bat %source_dir% %final_dir%
    
    echo.
    echo ====================================================
    echo   DONE! Results are in %final_dir%\out\
    echo ====================================================
) else (
    echo [ERROR] korres file was NOT created. Calculation failed.
    echo Please check %final_dir%\log_calc.txt and %final_dir%\korlis
)

echo.
echo Script finished. Press any key to exit...
pause >nul