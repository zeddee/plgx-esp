# Copyright 2020 EclecticIQ. All rights reserved.
# Use this script to perform upgrade on Polylogyx Agent prior to v2.0 via 
# Custom Script Execution on server. Update the server IP (line 12) below,
# agent administrator level username(line 13) and password(line 14) and push
# script to the agent.
#
# Platform: Windows x64

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::TLS12
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

$ip="<PROVIDE_SERVER_IP_HERE>"
$username="<PROVIDE_AGENT_USERNAME_HERE>"
$password="<PROVIDE_AGENT_PASSWORD_HERE>"

$RunLevel = "Highest"
$tempdir="c:\plgx-temp\"
$url = -join("https://", $ip, ":9000/downloads/windows/plgx_cpt.exe")
$output = -join($tempdir, "plgx_cpt_maint.exe")
$task = "Polylogyx Agent Maintenance"

if ($(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue).TaskName -eq $task)
{
    Unregister-ScheduledTask -TaskName $task -Confirm:$False
    write-output "Unregistered existing scheduled task '$task'"
}

if (-not (Test-Path -LiteralPath $tempdir)) 
{
    New-Item -Path $tempdir -ItemType Directory
    write-output "Created directory '$tempdir'"
}
else
{
    write-output "Directory '$tempdir' already exists !!"
}

try
{
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($url, $output)
}
catch
{
    write-error "Error while downloading file from server"
    Exit 1 
}

$action = New-ScheduledTaskAction -Execute $output -Argument "-g s"
$trigger =  New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(120) 

try
{
    Register-ScheduledTask -Action  $action -User $username -Password $password -RunLevel $RunLevel -Trigger $trigger -TaskName $task -Description $task
}
catch
{
    write-error "Failed creating '$task' scheduled task"
    Exit 3 
}

if ($(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue).TaskName -eq $task)
{
	write-output "Successfully created '$task' scheduled task !!"
}
