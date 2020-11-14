@echo off
REM Copyright 2020 EclecticIQ. All rights reserved.
REM Use this script to perform upgrade on Polylogyx Agent v2.0 via 
REM Custom Script Execution on server. Update the server IP on line 13 below
REM and push the script to the agent.
REM
REM Platform: Windows x64

REM Set local environment
setlocal

REM Example: set IP=10.10.10.10
SET IP=<SET_SERVER_IP_ADDRESS_HERE_WITHOUT_ENCLOSING_IN_QUOTES>

SET TEMPDIR=c:\plgx-temp
SET OUTPUT="%TEMPDIR%\plgx_cpt_maint.exe"
SET TASK="Polylogyx Agent Maintenance"
SET URL="https://%IP%:9000/downloads/windows/plgx_cpt.exe"

REM Delete existing task first (in case it exists)
schtasks /DELETE /TN %TASK% /F

REM Create temporary directory for downloading CPT
IF EXIST %TEMPDIR% (
    echo Directory %TEMPDIR% already exists !!
) ELSE (
    echo Creating Directory %TEMPDIR%...
    mkdir %TEMPDIR%
)

REM Download CPT from server in temporary directory
echo Download url set to: %URL%
curl --insecure -f -o %OUTPUT% %URL%
IF %ERRORLEVEL% NEQ 0 (
	    ECHO ERROR: Download failed. Exiting!!
        goto :eof
)
echo "CPT download successful !!"

:tryagain
REM Compute scheduled time for task (current time + 2 minutes)
SET CURRENTTIME=%TIME%
for /F "tokens=1 delims=:" %%h in ('echo %CURRENTTIME%') do (set /a HR=%%h)
for /F "tokens=2 delims=:" %%m in ('echo %CURRENTTIME%') do (set /a MIN=%%m + 2)

IF %ERRORLEVEL% NEQ 0 (
	    ECHO Probably Minute value is either 08 or 09 which is considered invalid **octal** number by DOS. !!
        ECHO Waiting a minute and trying again...
        TIMEOUT 60
        goto :tryagain
)

IF %MIN% GEQ 60 (
    SET /a MIN=%MIN%-60 
    SET /a HR=%HR%+1
)
IF %HR% GTR 24 SET HR=00

IF %MIN% LEQ 9 (
    SET MIN=0%MIN%
)

IF %HR% LEQ 9 (
    SET HR=0%HR%
)
SET NEWTIME=%HR%:%MIN%

REM Set command to run in scheduled task
SET ACTION="%OUTPUT% -g s"

schtasks /create /RU "NT AUTHORITY\SYSTEM" /TN %TASK% /TR %ACTION% /RL HIGHEST /SC ONCE /ST %NEWTIME% /F
IF %ERRORLEVEL% NEQ 0 (
	    ECHO ERROR: Failed to create scheduled task. Exiting!!
        goto :eof
)

:eof
endlocal
