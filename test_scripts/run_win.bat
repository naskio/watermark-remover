@echo off
SETLOCAL
set EXECUTABLE=%1
set FILENAME=%~nx1
set TIMEOUT=%2

echo executable is %EXECUTABLE%
echo filename is %FILENAME%
dir

@REM echo Starting %EXECUTABLE%...
@REM START "" %EXECUTABLE%

echo Waiting for %TIMEOUT% seconds..
timeout /T %TIMEOUT% /NOBREAK > NUL

tasklist /fi "ImageName eq %FILENAME%" /fo csv 2>NUL | find /I "%FILENAME%"> NUL
echo ERROR LEVEL is %ERRORLEVEL%

IF %ERRORLEVEL% NEQ 0 (
   echo Program %FILENAME% is not running
   echo Quitting %FILENAME%
   taskkill /f /im %FILENAME%
   echo failed with %ERRORLEVEL% 
   exit 1
) ELSE (
   echo Program %FILENAME% is running
   echo Quitting %FILENAME%
   taskkill /f /im %FILENAME%
   echo succeed with %ERRORLEVEL%
   exit 0
)
ENDLOCAL

echo END