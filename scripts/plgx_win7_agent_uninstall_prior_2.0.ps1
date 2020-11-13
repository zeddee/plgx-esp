# Copyright 2020 EclecticIQ. All rights reserved.
# Use this script to perform uninstall of Polylogyx Agent prior to v2.0 via 
# Custom Script Execution on server. Update the server IP (line 12) below,
# agent administrator level username(line 13) and password(line 14) and push
# script to the agent.
#
# Platform: Windows x64

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

$ip="<PROVIDE_SERVER_IP_HERE>"
$username="<PROVIDE_AGENT_USERNAME_HERE>"
$password="<PROVIDE_AGENT_PASSWORD_HERE>"

$RunLevel = "Highest"
$tempdir="c:\plgx-temp\"
$url = -join("https://", $ip, ":9000/downloads/windows/plgx_cpt.exe")
$output = -join($tempdir, "plgx_cpt_maint.exe")
$task = "Polylogyx Agent Maintenance"

schtasks /DELETE /TN $task /F
write-output "Unregistered existing scheduled task '$task'"

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

$action = -join($output, " -u s")
$time = [DateTime]::Now.AddMinutes(2)
$hourMinute=$time.ToString("HH:mm")

schtasks /create /RU $username /RP $password /TN $task /TR $action /RL HIGHEST /SC ONCE /ST $hourMinute /F
write-output "Successfully created '$task' scheduled task !!"
