@echo off
SETLOCAL
set EXECUTABLE=%1
set FILENAME=%~nx1
set TIMEOUT=%2

echo executable is %EXECUTABLE%
echo filename is %FILENAME%
dir

START %EXECUTABLE%
timeout /T %TIMEOUT% /NOBREAK > nul

tasklist /fi "ImageName eq %FILENAME%" /fo csv 2>NUL | find /I "%FILENAME%">NUL

echo ERROR LEVEL is %ERRORLEVEL% 
IF %ERRORLEVEL% NEQ 0 (
   echo Program %FILENAME% is not running
   taskkill /f /im %FILENAME%
   echo failed with %ERRORLEVEL% 
   exit 1
) ELSE (
   echo Program %FILENAME% is running
   taskkill /f /im %FILENAME%
   echo succeed with %ERRORLEVEL%
   exit 0
)
ENDLOCAL

echo END