@echo off
SETLOCAL
set EXECUTABLE=%1
set FILENAME=%~nx1
set TIMEOUT=%2

echo executable is %EXECUTABLE%.
echo filename is %FILENAME%.
dir

echo Starting %EXECUTABLE%...
IF NOT EXIST %EXECUTABLE% (
    echo %EXECUTABLE% is missing.
    exit 1
)
START "" %EXECUTABLE%

echo Waiting for %TIMEOUT% seconds...
echo Started waiting at %TIME%.
ping 127.0.0.1 -n %TIMEOUT% > NUL
echo Wait finished at %TIME%.

echo Checking if %FILENAME% is still running...
tasklist /fi "ImageName eq %FILENAME%" /fo csv 2>NUL | find /I "%FILENAME%"> NUL
echo ERROR LEVEL is %ERRORLEVEL%.

IF %ERRORLEVEL% NEQ 0 (
   echo Program %FILENAME% is not running.
   echo Trying to quit %FILENAME% even if not running...
   taskkill /f /im %FILENAME%
   echo Failed: EXE failed with code %ERRORLEVEL% .
   exit 1
) ELSE (
   echo Program %FILENAME% is running.
   echo Quitting %FILENAME%...
   taskkill /f /im %FILENAME%
   echo Success: EXE succeeded with code %ERRORLEVEL%.
   exit 0
)
ENDLOCAL

echo END