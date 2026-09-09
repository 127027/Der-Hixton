function Invoke-HixtonNativeCodex {
    param(
        [Parameter(Mandatory=$true)][string]$CodexPath,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [string]$InputText
    )

    # Windows PowerShell 5.1 can turn a native program's stderr into a
    # NativeCommandError when the caller uses ErrorActionPreference=Stop.
    # Codex intentionally writes "Not logged in" to stderr, so capture the
    # native exit code ourselves instead of letting PowerShell terminate.
    $oldPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        if ($PSBoundParameters.ContainsKey('InputText')) {
            $raw = $InputText | & $CodexPath @Arguments 2>&1
        }
        else {
            $raw = & $CodexPath @Arguments 2>&1
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }

    $text = ($raw | ForEach-Object { $_.ToString() }) -join "`n"
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = $text
    }
}

function Get-HixtonNpmCodex {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw 'npm was not found. Install Node/npm before starting the Hixton agent.'
    }

    $prefix = (& npm config get prefix).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $prefix) {
        throw 'Could not determine the global npm prefix.'
    }

    $candidate = Join-Path $prefix 'codex.cmd'
    if (-not (Test-Path $candidate)) {
        throw "The npm Codex launcher was not found at $candidate. Run: npm install -g @openai/codex@latest"
    }

    return $candidate
}

function Invoke-HixtonApiLogin {
    param(
        [Parameter(Mandatory=$true)][string]$CodexPath,
        [Parameter(Mandatory=$true)][string]$CodexHome
    )

    New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
    $env:CODEX_HOME = $CodexHome

    if ($env:OPENAI_API_KEY) {
        Write-Host 'Using OPENAI_API_KEY from the local process environment for the isolated Hixton Codex login.'
        $result = Invoke-HixtonNativeCodex -CodexPath $CodexPath -Arguments @('login','--with-api-key') -InputText $env:OPENAI_API_KEY
        if ($result.ExitCode -ne 0) {
            throw "Codex API-key login failed.`n$($result.Output)"
        }
        Write-Host $result.Output
        return
    }

    Write-Host ''
    Write-Host 'One-time local API login is required for the Hixton reserve agent.'
    Write-Host 'Paste the OpenAI API key here. Input is hidden and is NOT written to the repository or command history.'
    Write-Host 'Codex stores its local authentication only inside the isolated profile under LOCALAPPDATA\HixtonAgent\codex-api.'
    $secure = Read-Host 'OpenAI API key' -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = $null
    try {
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        if ([string]::IsNullOrWhiteSpace($plain)) { throw 'No API key was entered.' }
        $result = Invoke-HixtonNativeCodex -CodexPath $CodexPath -Arguments @('login','--with-api-key') -InputText $plain
        if ($result.ExitCode -ne 0) {
            throw "Codex API-key login failed.`n$($result.Output)"
        }
        Write-Host $result.Output
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        $plain = $null
        $secure = $null
    }
}

function Initialize-HixtonApiCodex {
    param(
        [Parameter(Mandatory=$true)][string]$AgentRoot
    )

    $codexPath = Get-HixtonNpmCodex
    $codexHome = Join-Path $AgentRoot 'codex-api'
    New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
    $env:CODEX_HOME = $codexHome

    $versionResult = Invoke-HixtonNativeCodex -CodexPath $codexPath -Arguments @('--version')
    if ($versionResult.ExitCode -ne 0) { throw 'Could not start the npm Codex CLI.' }
    Write-Host "Hixton Codex CLI: $($versionResult.Output)"
    Write-Host "Isolated Codex profile: $codexHome"

    $statusResult = Invoke-HixtonNativeCodex -CodexPath $codexPath -Arguments @('login','status')
    if ($statusResult.ExitCode -ne 0) {
        Write-Host 'Hixton API profile is not logged in yet.'
        Invoke-HixtonApiLogin -CodexPath $codexPath -CodexHome $codexHome
        $statusResult = Invoke-HixtonNativeCodex -CodexPath $codexPath -Arguments @('login','status')
        if ($statusResult.ExitCode -ne 0) {
            throw "Codex login still is not valid after the local API-key login.`n$($statusResult.Output)"
        }
    }

    Write-Host $statusResult.Output
    Write-Host 'Hixton Codex authentication is ready in the isolated local profile.'
    return [PSCustomObject]@{
        CodexPath = $codexPath
        CodexHome = $codexHome
    }
}
