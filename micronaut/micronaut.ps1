# MICRONAUT ORCHESTRATOR (SCO/1 projection only)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$IO = Join-Path $Root "io"
$Chat = Join-Path $IO "chat.txt"
$Stream = Join-Path $IO "stream.txt"

$State = "INIT"
Write-Host "Micronaut online."
$State = "READY"

$lastSize = 0

function Invoke-CM1Verify {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Entry
    )

    $command = Get-Command cm1_verify -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        Write-Host "CM-1 verifier unavailable."
        return $false
    }

    $result = & $command $Entry
    return [bool]$result
}

function Invoke-KUHUL-TSG {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Input
    )

    $command = Get-Command kuhul_tsg -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "KUHUL-TSG μ-op unavailable."
    }

    return & $command $Input
}

function Invoke-SCXQ2-Infer {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Signal
    )

    $command = Get-Command scxq2_infer -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "SCXQ2 μ-op unavailable."
    }

    return & $command $Signal
}

while ($true) {
    if (Test-Path $Chat) {
        $size = (Get-Item $Chat).Length
        if ($size -gt $lastSize) {
            $State = "RUNNING"

            $entry = Get-Content $Chat -Raw
            $lastSize = $size

            # ---- CM-1 VERIFY ----
            if (-not (Invoke-CM1Verify -Entry $entry)) {
                Write-Host "CM-1 violation"
                $State = "HALT"
                break
            }

            # ---- SEMANTIC EXTRACTION ----
            $signal = Invoke-KUHUL-TSG -Input $entry

            # ---- INFERENCE (SEALED) ----
            $response = Invoke-SCXQ2-Infer -Signal $signal

            # ---- STREAM OUTPUT ----
            $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
            Add-Content $Stream ">> t=$timestamp ctx=@π mass=0.0"
            Add-Content $Stream $response

            $State = "IDLE"
        }
    }

    Start-Sleep -Milliseconds 200
}
