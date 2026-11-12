[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [ValidateRange(15, 600)]
    [int]$StartupTimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = $PSScriptRoot
$RuntimeRoot = Join-Path $ProjectRoot 'runtime'
$LogRoot = Join-Path $RuntimeRoot 'logs'
$PidFile = Join-Path $RuntimeRoot 'starfall-processes.json'
$StartedProcesses = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
$ComponentResults = [System.Collections.Generic.List[object]]::new()

function Write-Stage {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Set-DefaultEnvironment {
    param([string]$Name, [string]$Value)
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($Name, 'Process'))) {
        [Environment]::SetEnvironmentVariable($Name, $Value, 'Process')
    }
}

function Test-PythonExecutable {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }
    if ($Path -like '*\Microsoft\WindowsApps\python*.exe') {
        return $false
    }

    try {
        $null = & $Path -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Resolve-PythonExecutable {
    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($candidate in @(
        $env:STARFALL_PYTHON,
        (Join-Path $ProjectRoot '.venv\Scripts\python.exe'),
        (Join-Path $ProjectRoot 'venv\Scripts\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe')
    )) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            $candidates.Add($candidate)
        }
    }

    foreach ($pattern in @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python*\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Python\pythoncore-*\python.exe')
    )) {
        Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object { $candidates.Add($_.FullName) }
    }

    $pathCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($null -ne $pathCommand) {
        $candidates.Add($pathCommand.Source)
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-PythonExecutable -Path $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw @"
Python 3.10+ was not found. Install Python and the Starfall packages, or set
STARFALL_PYTHON to a working python.exe. Then run:
  python -m pip install -r "$ProjectRoot\MLSimulator\requirements.txt"
"@
}

function Resolve-MavenExecutable {
    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($candidate in @(
        $env:STARFALL_MAVEN,
        (Join-Path $ProjectRoot 'mvnw.cmd')
    )) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            $candidates.Add($candidate)
        }
    }

    foreach ($name in @('mvn.cmd', 'mvn.exe', 'mvn')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            $candidates.Add($command.Source)
        }
    }

    Get-ChildItem -Path (Join-Path $ProjectRoot '.tools\apache-maven-*\bin\mvn.cmd') -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object { $candidates.Add($_.FullName) }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw 'Apache Maven was not found. Install Maven or set STARFALL_MAVEN to mvn.cmd.'
}

function Resolve-JavaExecutable {
    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($candidate in @(
        $env:STARFALL_JAVA,
        $(if (-not [string]::IsNullOrWhiteSpace($env:JAVA_HOME)) { Join-Path $env:JAVA_HOME 'bin\java.exe' })
    )) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            $candidates.Add($candidate)
        }
    }

    Get-ChildItem -Path (Join-Path $ProjectRoot '.tools\jdk-*\bin\java.exe') -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object { $candidates.Add($_.FullName) }

    $pathCommand = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($null -ne $pathCommand) {
        $candidates.Add($pathCommand.Source)
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw 'Java was not found. Install JDK 23 or set STARFALL_JAVA to java.exe.'
}

function Assert-PythonPackages {
    param([string]$Python)
    $probeOutput = @()
    $probeExitCode = 1
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        # Native stderr must be captured as diagnostic text instead of becoming
        # a terminating PowerShell error that hides the real Python exception.
        $ErrorActionPreference = 'Continue'
        $probeOutput = @(& $Python -c "import flask, qiskit" 2>&1)
        $probeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($probeExitCode -ne 0) {
        $details = ($probeOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
        if ([string]::IsNullOrWhiteSpace($details)) {
            $details = 'Python returned no diagnostic output.'
        }
        $installCommand = "`"$Python`" -m pip install -r `"$ProjectRoot\MLSimulator\requirements.txt`""
        throw "Python dependencies are incomplete.`n$details`nRepair command:`n  $installCommand"
    }
}

function Get-MySqlService {
    $service = $null
    if (-not [string]::IsNullOrWhiteSpace($env:STARFALL_MYSQL_SERVICE)) {
        $service = Get-Service -Name $env:STARFALL_MYSQL_SERVICE -ErrorAction SilentlyContinue
    }
    if ($null -eq $service) {
        $service = Get-Service -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^(mysql|maria)' -or $_.DisplayName -match 'MySQL|MariaDB' } |
            Select-Object -First 1
    }
    if ($null -eq $service) {
        throw 'No MySQL or MariaDB Windows service was found.'
    }
    return $service
}

function Start-MySqlIfNeeded {
    $service = Get-MySqlService
    if ($service.Status -eq 'Running') {
        Write-Host "MySQL service $($service.Name) is already running." -ForegroundColor DarkGreen
        return
    }

    Write-Host "Starting MySQL service $($service.Name)..."
    try {
        Start-Service -Name $service.Name -ErrorAction Stop
    }
    catch {
        $escapedName = $service.Name.Replace("'", "''")
        $command = "Start-Service -Name '$escapedName' -ErrorAction Stop"
        $elevated = Start-Process -FilePath 'powershell.exe' -ArgumentList @(
            '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $command
        ) -Verb RunAs -WindowStyle Hidden -Wait -PassThru
        if ($elevated.ExitCode -ne 0) {
            throw "MySQL service $($service.Name) could not be started."
        }
    }

    $service = Get-Service -Name $service.Name
    $service.WaitForStatus('Running', [TimeSpan]::FromSeconds(30))
    Write-Host "MySQL service $($service.Name) is ready." -ForegroundColor Green
}

function Test-HttpReady {
    param([string]$Uri)
    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
    }
    catch {
        return $false
    }
}

function Get-PortOwnerDescription {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop | Select-Object -First 1
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        if ($null -ne $process) {
            return "$($process.ProcessName) (PID $($process.Id))"
        }
        return "PID $($connection.OwningProcess)"
    }
    catch {
        return $null
    }
}

function Start-StarfallComponent {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$HealthUri,
        [int]$Port
    )

    if (Test-HttpReady -Uri $HealthUri) {
        Write-Host "$Name is already healthy at $HealthUri" -ForegroundColor DarkGreen
        $ComponentResults.Add([pscustomobject]@{ Component = $Name; Status = 'Already running'; PID = '-' })
        return
    }

    $portOwner = Get-PortOwnerDescription -Port $Port
    if ($null -ne $portOwner) {
        throw "$Name cannot start: port $Port is already used by $portOwner, but $HealthUri is not healthy."
    }

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $safeName = $Name.ToLowerInvariant().Replace(' ', '-')
    $stdoutLog = Join-Path $LogRoot "$safeName-$stamp.out.log"
    $stderrLog = Join-Path $LogRoot "$safeName-$stamp.err.log"
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -WindowStyle Hidden -PassThru
    $StartedProcesses.Add($process)

    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    do {
        if (Test-HttpReady -Uri $HealthUri) {
            Write-Host "$Name is ready at $HealthUri (PID $($process.Id))." -ForegroundColor Green
            $ComponentResults.Add([pscustomobject]@{ Component = $Name; Status = 'Started'; PID = $process.Id })
            return
        }

        $process.Refresh()
        if ($process.HasExited) {
            $process.WaitForExit()
            $process.Refresh()
            $stderrLines = if (Test-Path -LiteralPath $stderrLog) { @(Get-Content -LiteralPath $stderrLog -Tail 120 -ErrorAction SilentlyContinue) } else { @() }
            $stdoutLines = if (Test-Path -LiteralPath $stdoutLog) { @(Get-Content -LiteralPath $stdoutLog -Tail 160 -ErrorAction SilentlyContinue) } else { @() }
            $allLines = @($stderrLines) + @($stdoutLines)
            $credentialFailure = $allLines | Where-Object { $_ -match 'Access denied for user' } | Select-Object -Last 1
            if ($null -ne $credentialFailure) {
                $details = "Database authentication failed: $credentialFailure"
            }
            elseif ($stderrLines.Count -gt 0) {
                $details = ($stderrLines | Select-Object -Last 15) -join [Environment]::NewLine
            }
            elseif ($stdoutLines.Count -gt 0) {
                $details = ($stdoutLines | Select-Object -Last 15) -join [Environment]::NewLine
            }
            else {
                $details = 'No process output was produced.'
            }
            $exitCode = if ($null -eq $process.ExitCode -or [string]::IsNullOrWhiteSpace([string]$process.ExitCode)) { 'unavailable' } else { [string]$process.ExitCode }
            throw "$Name exited with code $exitCode.`n$details`nLogs: $stdoutLog and $stderrLog"
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)

    throw "$Name did not become healthy within $StartupTimeoutSeconds seconds. Logs: $stdoutLog and $stderrLog"
}

function Get-DatabasePassword {
    if (-not [string]::IsNullOrWhiteSpace($env:DB_PASSWORD)) {
        return
    }

    $securePassword = Read-Host 'MySQL password for the configured DB_USERNAME' -AsSecureString
    if ($securePassword.Length -eq 0) {
        throw 'DB_PASSWORD is required. It was not saved or hardcoded.'
    }
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    try {
        $env:DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

function Stop-StartedProcesses {
    foreach ($process in $StartedProcesses) {
        try {
            if (-not $process.HasExited) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
        catch {
            # Only best-effort cleanup of processes launched by this invocation.
        }
    }
}

try {
    if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot 'pom.xml'))) {
        throw "Start-Starfall.ps1 must remain in the Project Starfall repository root."
    }

    Write-Stage 'Checking Starfall prerequisites'
    $python = Resolve-PythonExecutable
    Assert-PythonPackages -Python $python
    $maven = Resolve-MavenExecutable
    $java = Resolve-JavaExecutable
    $javaBin = Split-Path -Parent $java
    $env:JAVA_HOME = Split-Path -Parent $javaBin
    $env:Path = "$javaBin;$env:Path"
    $mysqlService = Get-MySqlService

    Write-Host "Python : $python"
    Write-Host "Maven  : $maven"
    Write-Host "Java   : $java"
    Write-Host "MySQL  : $($mysqlService.Name) [$($mysqlService.Status)]"

    if ($ValidateOnly) {
        Write-Host "`nValidation complete. No services were started." -ForegroundColor Green
        exit 0
    }

    New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

    Set-DefaultEnvironment -Name 'DB_URL' -Value 'jdbc:mysql://127.0.0.1:3306/aegis'
    Set-DefaultEnvironment -Name 'DB_USERNAME' -Value 'root'
    Set-DefaultEnvironment -Name 'DB_SCHEMA_ACTION' -Value 'validate'
    Set-DefaultEnvironment -Name 'HOST' -Value '127.0.0.1'
    Set-DefaultEnvironment -Name 'PORT' -Value '5000'
    Set-DefaultEnvironment -Name 'AGENT_HOST' -Value '127.0.0.1'
    Set-DefaultEnvironment -Name 'AGENT_PORT' -Value '5001'
    Set-DefaultEnvironment -Name 'SERVER_PORT' -Value '8080'
    Set-DefaultEnvironment -Name 'STARFALL_FRONTEND_PORT' -Value '5500'
    $analysisPort = [int]$env:PORT
    $agentPort = [int]$env:AGENT_PORT
    $backendPort = [int]$env:SERVER_PORT
    $frontendPort = [int]$env:STARFALL_FRONTEND_PORT
    Set-DefaultEnvironment -Name 'PYTHON_SERVICE_URL' -Value "http://127.0.0.1:$analysisPort"
    Set-DefaultEnvironment -Name 'AGENT_SERVICE_URL' -Value "http://127.0.0.1:$agentPort"
    Set-DefaultEnvironment -Name 'APP_CORS_ALLOWED_ORIGINS' -Value "http://127.0.0.1:$frontendPort,http://localhost:$frontendPort"
    Set-DefaultEnvironment -Name 'FLASK_DEBUG' -Value 'false'
    Set-DefaultEnvironment -Name 'AI_AGENT_FALLBACK_ENABLED' -Value 'true'
    Set-DefaultEnvironment -Name 'PYTHONUNBUFFERED' -Value '1'
    Get-DatabasePassword

    Write-Stage 'Starting database'
    Start-MySqlIfNeeded

    Write-Stage 'Starting Spring Boot API and validating database access'
    $mavenRepository = Join-Path $ProjectRoot '.tools\m2-repository'
    Start-StarfallComponent -Name 'Spring Boot API' -Executable $maven `
        -Arguments @('-q', "-Dmaven.repo.local=$mavenRepository", 'org.springframework.boot:spring-boot-maven-plugin:3.2.4:run') -WorkingDirectory $ProjectRoot `
        -HealthUri "http://127.0.0.1:$backendPort/api/v1/health" -Port $backendPort

    Write-Stage 'Starting AI decision agent'
    Start-StarfallComponent -Name 'Agent service' -Executable $python `
        -Arguments @('-m', 'AgentService.App') -WorkingDirectory $ProjectRoot `
        -HealthUri "http://127.0.0.1:$agentPort/internal/v1/health" -Port $agentPort

    Write-Stage 'Starting simulation and quantum service'
    Start-StarfallComponent -Name 'Analysis and quantum service' -Executable $python `
        -Arguments @('MLSimulator/App.py') -WorkingDirectory $ProjectRoot `
        -HealthUri "http://127.0.0.1:$analysisPort/internal/v1/health" -Port $analysisPort

    Write-Stage 'Starting frontend'
    Start-StarfallComponent -Name 'Frontend' -Executable $python `
        -Arguments @('-m', 'http.server', "$frontendPort", '--bind', '127.0.0.1', '--directory', 'Frontend') -WorkingDirectory $ProjectRoot `
        -HealthUri "http://127.0.0.1:$frontendPort/" -Port $frontendPort

    $StartedProcesses |
        ForEach-Object { [pscustomobject]@{ PID = $_.Id; StartedAt = (Get-Date).ToString('o') } } |
        ConvertTo-Json | Set-Content -LiteralPath $PidFile -Encoding UTF8

    Write-Stage 'Starfall is ready'
    $ComponentResults | Format-Table -AutoSize
    Write-Host "Logs: $LogRoot"
    $frontendUrl = "http://127.0.0.1:$frontendPort/"
    Write-Host "Opening $frontendUrl"
    try {
        Start-Process $frontendUrl
    }
    catch {
        Write-Host 'The services are ready, but the browser could not be opened automatically.' -ForegroundColor Yellow
    }
}
catch {
    Stop-StartedProcesses
    Write-Host "`nStarfall startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Any components started by this run were stopped. Existing services were left untouched." -ForegroundColor Yellow
    exit 1
}
