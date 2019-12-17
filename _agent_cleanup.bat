@echo off

NET SESSION >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
REM    ECHO Administrator PRIVILEGES Detected! 
) ELSE (
   echo ######## ########  ########   #######  ########  
   echo ##       ##     ## ##     ## ##     ## ##     ## 
   echo ##       ##     ## ##     ## ##     ## ##     ## 
   echo ######   ########  ########  ##     ## ########  
   echo ##       ##   ##   ##   ##   ##     ## ##   ##   
   echo ##       ##    ##  ##    ##  ##     ## ##    ##  
   echo ######## ##     ## ##     ##  #######  ##     ## 
   echo.
   echo.
   echo ####### ERROR: ADMINISTRATOR PRIVILEGES REQUIRED #########
   echo This script must be run as administrator to work properly!  
   echo ##########################################################
   echo.
   PAUSE
   EXIT /B 1
)


echo "Uninstalling osquery agent...please wait"
REM uninstall osqueryd from msi guid (3.2.6), if exists
MsiExec.exe /q /x {A00B7823-A9A3-4577-A804-A07C43765AFD} >nul 2>&1
REM timeout /t 3 /nobreak >nul 2>&1

REM uninstall osqueryd from msi guid (4.2.0), if exists
MsiExec.exe /q /x {A5D07D11-B347-4B04-BD8C-994E28502D30} >nul 2>&1
REM timeout /t 3 /nobreak >nul 2>&1

echo "Stopping all the services..."

for /F "tokens=3 delims=: " %%H in ('sc query "osqueryd" ^| findstr "        STATE"') do (
  if /I "%%H" EQU "RUNNING" (
   REM Stop osqueryd service
   sc stop osqueryd >nul 2>&1
   timeout /t 3 /nobreak >nul 2>&1
   sc query osqueryd | find "STOPPED"
   if errorlevel 1 (
      timeout /t 3 /nobreak >nul 2>&1
    )
  )
)

for /F "tokens=3 delims=: " %%H in ('sc query "plgx_cpt" ^| findstr "        STATE"') do (
  if /I "%%H" EQU "RUNNING" (
   REM Stop plgx_cpt service
   sc stop plgx_cpt >nul 2>&1
   timeout /t 3 /nobreak >nul 2>&1
   sc query plgx_cpt | find "STOPPED" >nul 2>&1
   if errorlevel 1 (
      timeout /t 3 /nobreak >nul 2>&1
    )
  )
)

sc delete osqueryd >nul 2>&1
sc delete plgx_cpt >nul 2>&1

timeout /t 2 /nobreak >nul 2>&1

echo "Cleaning the osqueryd files.."

if exist "C:\ProgramData\osquery\" (
takeown /F "C:\ProgramData\osquery" /R /A /D y >nul 2>&1
rmdir /S /Q "C:\ProgramData\osquery" >nul 2>&1
)

if exist "C:\Program Files\osquery\" (
takeown /F "C:\Program Files\osquery" /R /A /D y >nul 2>&1
rmdir /S /Q "C:\Program Files\osquery" >nul 2>&1
)

timeout /t 5 /nobreak >nul 2>&1

REM clean_extension
echo "Cleaning the Extension.."
REM Clean up the extension db
rmdir /S /Q C:\ProgramData\plgx_win_extension >nul 2>&1

REM Clean up the drivers
fltmc unload vast >nul 2>&1
sc delete vast >nul 2>&1
del /F /Q /S C:\Windows\System32\drivers\vast.sys >nul 2>&1
sc stop vastnw >nul 2>&1
sc delete vastnw >nul 2>&1
del /F /Q /S C:\Windows\System32\drivers\vastnw.sys >nul 2>&1

echo "Clean up done."