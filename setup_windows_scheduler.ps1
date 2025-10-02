# Network Logging - PowerShell Setup Script for Windows Task Scheduler
# Run this to set up automated monitoring

Write-Host "=== Network Logging - Windows Setup ===" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WrapperScript = Join-Path $ScriptDir "start_netlogging.bat"
$ConfigFile = Join-Path $ScriptDir "config.json"

# Check if config exists
if (-not (Test-Path $ConfigFile)) {
    Write-Host "ERROR: config.json not found!" -ForegroundColor Red
    Write-Host "Please copy config.example.json to config.json and configure it." -ForegroundColor Yellow
    exit 1
}

# Check if wrapper script exists
if (-not (Test-Path $WrapperScript)) {
    Write-Host "ERROR: start_netlogging.bat not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Configuration found. Now let's set up the Task Scheduler..." -ForegroundColor Green
Write-Host ""

# Prompt for interval
Write-Host "How often should network monitoring run?" -ForegroundColor Yellow
Write-Host "1) Every 1 minute (recommended)"
Write-Host "2) Every 2 minutes"
Write-Host "3) Every 5 minutes"
Write-Host "4) Every 10 minutes"
Write-Host "5) Custom interval"
$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    "1" { $interval = "PT1M"; $description = "every minute" }
    "2" { $interval = "PT2M"; $description = "every 2 minutes" }
    "3" { $interval = "PT5M"; $description = "every 5 minutes" }
    "4" { $interval = "PT10M"; $description = "every 10 minutes" }
    "5" { 
        $minutes = Read-Host "Enter interval in minutes"
        $interval = "PT${minutes}M"
        $description = "every $minutes minutes"
    }
    default { 
        Write-Host "Invalid choice. Using 1 minute interval." -ForegroundColor Yellow
        $interval = "PT1M"
        $description = "every minute"
    }
}

Write-Host ""
Write-Host "Creating Task Scheduler entry for network monitoring ($description)..." -ForegroundColor Green

# Create Task Scheduler task
$taskName = "NetworkLogging"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$WrapperScript`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval $interval -RepetitionDuration ([TimeSpan]::MaxValue)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

try {
    # Remove existing task if it exists
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Register new task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Network connectivity monitoring and logging" | Out-Null
    
    Write-Host ""
    Write-Host "SUCCESS! Task Scheduler configured!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task name: $taskName" -ForegroundColor Cyan
    Write-Host "Interval: $description" -ForegroundColor Cyan
    Write-Host "Log file: $ScriptDir\logs\cron.log" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view/manage the task:"
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for '$taskName' in Task Scheduler Library"
    Write-Host ""
    Write-Host "To start monitoring immediately:"
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To remove the task:"
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Yellow
}
catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create Task Scheduler task" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Setup complete! Network monitoring is now active." -ForegroundColor Green
Write-Host "Check logs\cron.log for monitoring output." -ForegroundColor Green
