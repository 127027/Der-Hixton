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
        Write-Host 'Using OPENAI_API_KEY from the local process environment for one-time Codex API login.'
        $env:OPENAI_API_KEY | & $CodexPath login --with-api-key
        if ($LASTEXITCODE -ne 0) { throw 'Codex API-key login failed.' }
        return
    }

    Write-Host ''
    Write-Host 'One-time local API login is required for the Hixton reserve agent.'
    Write-Host 'Paste the OpenAI API key here. Input is hidden and is NOT written to the repository or command history.'
    $secure = Read-Host 'OpenAI API key' -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        if ([string]::IsNullOrWhiteSpace($plain)) { throw 'No API key was entered.' }
        $plain | & $CodexPath login --with-api-key
        if ($LASTEXITCODE -ne 0) { throw 'Codex API-key login failed.' }
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

    $version = (& $codexPath --version 2>&1) -join ' '
    if ($LASTEXITCODE -ne 0) { throw 'Could not start the npm Codex CLI.' }
    Write-Host "Hixton Codex CLI: $version"
    Write-Host "Isolated Codex profile: $codexHome"

    $statusOutput = (& $codexPath login status 2>&1) -join "`n"
    $statusCode = $LASTEXITCODE
    if ($statusCode -ne 0) {
        Invoke-HixtonApiLogin -CodexPath $codexPath -CodexHome $codexHome
        $statusOutput = (& $codexPath login status 2>&1) -join "`n"
        if ($LASTEXITCODE -ne 0) {
            throw 'Codex login still is not valid after the local API-key login.'
        }
    }

    Write-Host 'Hixton Codex authentication is ready in the isolated local profile.'
    return [PSCustomObject]@{
        CodexPath = $codexPath
        CodexHome = $codexHome
    }
}
