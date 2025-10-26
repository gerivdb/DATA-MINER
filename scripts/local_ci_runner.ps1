#!/usr/bin/env pwsh
# scripts/local_ci_runner.ps1
# Runner CI/CD local PowerShell pour DATA-MINER
# Alternative aux GitHub Actions avec exécution locale PC

<#
.SYNOPSIS
    Runner CI/CD local pour DATA-MINER évitant GitHub Actions payants
.DESCRIPTION
    Exécute les pipelines MSR localement sur PC avec intégration DevTools Hub
    et orchestration ECOYSTEM. Scheduling via PowerShell + Windows Task Scheduler.
.PARAMETER Action
    Action à exécuter (start-runner, stop-runner, execute-job, status)
.PARAMETER JobName
    Nom du job spécifique à exécuter
.PARAMETER Schedule
    Planification du runner (daily, hourly, manual)
.EXAMPLE
    .\local_ci_runner.ps1 -Action start-runner -Schedule daily
.EXAMPLE
    .\local_ci_runner.ps1 -Action execute-job -JobName "ecosystem-mining"
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("start-runner", "stop-runner", "execute-job", "status", "install-scheduler")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [string]$JobName,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("manual", "hourly", "daily", "weekly")]
    [string]$Schedule = "manual",
    
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "config/go_runner.json",
    
    [Parameter(Mandatory = $false)]
    [string]$LogPath = "./logs/runner",
    
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$RunnerID = "data-miner-local-ps1"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Création répertoires
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

# Fonction logging
function Write-RunnerLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] [$RunnerID] $Message"
    if ($Verbose -or $Level -eq "ERROR") {
        Write-Host $logEntry
    }
    Add-Content -Path "$LogPath/runner-$Timestamp.log" -Value $logEntry -Encoding UTF8
}

# Jobs DATA-MINER prédéfinis
$DataMinerJobs = @{
    "ecosystem-mining" = @{
        "name" = "Mining complet ECOSYSTEM-1"
        "command" = "python"
        "args" = @("-u", "scripts/ecosystem_mining.py", "--comprehensive")
        "timeout" = 1800  # 30 minutes
        "schedule" = "daily"
        "dependencies" = @("python", "pip")
    }
    "governance-report" = @{
        "name" = "Rapport governance anti-patterns"
        "command" = "python"
        "args" = @("-u", "src/governance/ci_gatekeeper.py", "--generate-report")
        "timeout" = 600   # 10 minutes
        "schedule" = "daily"
        "dependencies" = @("python")
    }
    "dashboard-update" = @{
        "name" = "Mise à jour données dashboard"
        "command" = "python"
        "args" = @("-u", "dashboards/ecosystem_dashboard.py", "--update-data")
        "timeout" = 300   # 5 minutes
        "schedule" = "hourly"
        "dependencies" = @("python", "streamlit")
    }
    "sync-devtools" = @{
        "name" = "Synchronisation DevTools Hub"
        "command" = "make"
        "args" = @("sync-devtools")
        "timeout" = 900   # 15 minutes
        "schedule" = "hourly"
        "dependencies" = @("make", "git")
    }
    "antipatterns-scan" = @{
        "name" = "Scan anti-patterns cross-repos"
        "command" = "python"
        "args" = @("-u", "src/analyzers/antipattern_detector.py", "--scan-all")
        "timeout" = 1200  # 20 minutes
        "schedule" = "daily"
        "dependencies" = @("python")
    }
}

# Fonction exécution job
function Invoke-DataMinerJob {
    param(
        [string]$JobID,
        [hashtable]$JobConfig
    )
    
    Write-RunnerLog "Démarrage job: $($JobConfig.name) ($JobID)"
    $startTime = Get-Date
    
    try {
        # Vérification dépendances
        foreach ($dep in $JobConfig.dependencies) {
            if (-not (Get-Command $dep -ErrorAction SilentlyContinue)) {
                throw "Dépendance manquante: $dep"
            }
        }
        
        # Préparation commande
        $process = Start-Process -FilePath $JobConfig.command -ArgumentList $JobConfig.args -NoNewWindow -PassThru -Wait
        
        $duration = (Get-Date) - $startTime
        
        if ($process.ExitCode -eq 0) {
            Write-RunnerLog "SUCCÈS job $JobID (durée: $($duration.TotalSeconds)s)"
            return @{ "status" = "success"; "duration" = $duration.TotalSeconds }
        } else {
            Write-RunnerLog "ÉCHEC job $JobID - Exit code: $($process.ExitCode)" -Level "ERROR"
            return @{ "status" = "failed"; "exit_code" = $process.ExitCode; "duration" = $duration.TotalSeconds }
        }
        
    } catch {
        $duration = (Get-Date) - $startTime
        Write-RunnerLog "ERREUR job $JobID: $($_.Exception.Message)" -Level "ERROR"
        return @{ "status" = "error"; "error" = $_.Exception.Message; "duration" = $duration.TotalSeconds }
    }
}

# Fonction installation Task Scheduler Windows
function Install-WindowsScheduler {
    Write-RunnerLog "Installation planification Windows Task Scheduler..."
    
    foreach ($jobID in $DataMinerJobs.Keys) {
        $job = $DataMinerJobs[$jobID]
        $taskName = "DataMiner-$jobID"
        
        # Définition trigger selon schedule
        $trigger = switch ($job.schedule) {
            "daily" { New-ScheduledTaskTrigger -Daily -At "02:00" }
            "hourly" { New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue) }
            "weekly" { New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "02:00" }
            default { $null }
        }
        
        if ($trigger) {
            # Action PowerShell
            $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File `"$PSCommandPath`" -Action execute-job -JobName `"$jobID`""
            
            # Settings
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            
            # Création/mise à jour tâche
            try {
                Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Force
                Write-RunnerLog "Tâche planifiée créée: $taskName ($($job.schedule))"
            } catch {
                Write-RunnerLog "Erreur création tâche $taskName: $($_.Exception.Message)" -Level "ERROR"
            }
        }
    }
}

# Fonction status runner
function Get-RunnerStatus {
    Write-Host ""
    Write-Host "=== DATA-MINER LOCAL RUNNER STATUS ===" -ForegroundColor Blue
    Write-Host "Runner ID: $RunnerID" -ForegroundColor Cyan
    Write-Host "Workspace: $(Get-Location)" -ForegroundColor Cyan
    Write-Host "Logs: $LogPath" -ForegroundColor Cyan
    
    Write-Host "
Jobs configurés:" -ForegroundColor Yellow
    foreach ($jobID in $DataMinerJobs.Keys) {
        $job = $DataMinerJobs[$jobID]
        Write-Host "  • $jobID - $($job.name) [$($job.schedule)]" -ForegroundColor Gray
    }
    
    # Vérification tâches Windows
    Write-Host "
Tâches Windows planifiées:" -ForegroundColor Yellow
    try {
        $tasks = Get-ScheduledTask -TaskPath "\" | Where-Object { $_.TaskName -like "DataMiner-*" }
        if ($tasks) {
            foreach ($task in $tasks) {
                $state = $task.State
                $color = if ($state -eq "Ready") { "Green" } else { "Red" }
                Write-Host "  • $($task.TaskName): $state" -ForegroundColor $color
            }
        } else {
            Write-Host "  Aucune tâche planifiée trouvée" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Erreur lecture tâches: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Fonction principale
function Main {
    try {
        Write-RunnerLog "Action demandée: $Action"
        
        switch ($Action) {
            "start-runner" {
                Write-RunnerLog "Démarrage DATA-MINER Local Runner"
                Write-Host "🚀 Démarrage DATA-MINER Local Runner..." -ForegroundColor Green
                
                # Installation planificateur si nécessaire
                if ($Schedule -ne "manual") {
                    Install-WindowsScheduler
                }
                
                Write-Host "✅ Runner local configuré et actif" -ForegroundColor Green
                Get-RunnerStatus
            }
            
            "execute-job" {
                if (-not $JobName -or -not $DataMinerJobs.ContainsKey($JobName)) {
                    throw "Job invalide ou manquant: $JobName"
                }
                
                $jobConfig = $DataMinerJobs[$JobName]
                $result = Invoke-DataMinerJob -JobID $JobName -JobConfig $jobConfig
                
                Write-Host "Résultat job $JobName : $($result.status)" -ForegroundColor $(if ($result.status -eq "success") { "Green" } else { "Red" })
            }
            
            "status" {
                Get-RunnerStatus
            }
            
            "stop-runner" {
                Write-RunnerLog "Arrêt DATA-MINER Local Runner"
                
                # Désactivation tâches planifiées
                try {
                    $tasks = Get-ScheduledTask -TaskPath "\" | Where-Object { $_.TaskName -like "DataMiner-*" }
                    foreach ($task in $tasks) {
                        Disable-ScheduledTask -TaskName $task.TaskName -Confirm:$false
                        Write-RunnerLog "Tâche désactivée: $($task.TaskName)"
                    }
                } catch {
                    Write-RunnerLog "Erreur désactivation tâches: $($_.Exception.Message)" -Level "ERROR"
                }
                
                Write-Host "⏹️ Runner local arrêté" -ForegroundColor Yellow
            }
            
            "install-scheduler" {
                Install-WindowsScheduler
                Write-Host "📅 Planificateur Windows installé" -ForegroundColor Green
            }
        }
        
    } catch {
        Write-RunnerLog "Erreur exécution: $($_.Exception.Message)" -Level "ERROR"
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Exécution
if ($MyInvocation.InvocationName -ne '.') {
    Main
}