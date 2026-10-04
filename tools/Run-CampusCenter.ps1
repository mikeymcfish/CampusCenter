[CmdletBinding()]
param(
    [ValidateSet('Vive', 'Desktop')][string]$Build = 'Vive',
    [switch]$PrepareOnly,
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.IO.Compression.FileSystem
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pins = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'CampusCenter-R28-downloads.json') -Raw | ConvertFrom-Json
$spec = $pins.builds.$Build
$buildCode = if ($Build -eq 'Vive') { 'v' } else { 'd' }
# Unreal's DLL loader still uses relative paths subject to Windows MAX_PATH.
$buildRoot = Join-Path $repoRoot ('.cc\r28\' + $buildCode)
$cacheRoot = Join-Path $buildRoot 'dl'
$expanded = Join-Path $buildRoot 'w'
$staging = Join-Path $buildRoot 'w.partial'
$legacyRoot = Join-Path $repoRoot ('.campuscenter-runtime\' + $pins.tag + '\' + $Build)
$lock = $null

function Hash-File([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
function Matches-Pin([string]$Path, $Pin) {
    return ((Test-Path -LiteralPath $Path -PathType Leaf) -and (Get-Item -LiteralPath $Path).Length -eq [long]$Pin.bytes -and (Hash-File $Path) -eq $Pin.sha256)
}
function Preserve-Invalid([string]$Path) {
    # Only this script's exact cache/staging paths are passed here. Never delete user files.
    if (Test-Path -LiteralPath $Path) {
        $saved = $Path + '.invalid.' + [Guid]::NewGuid().ToString('N')
        if ($Path.StartsWith(([IO.Path]::GetFullPath($staging).TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) {
            $quarantine = Join-Path $buildRoot 'invalid-staging-files'
            New-Item -ItemType Directory -Path $quarantine -Force | Out-Null
            $saved = Join-Path $quarantine ([Guid]::NewGuid().ToString('N') + '-' + [IO.Path]::GetFileName($Path))
        }
        Move-Item -LiteralPath $Path -Destination $saved
        Write-Host "Preserved invalid cache at $saved"
    }
}
function Get-Pinned($Pin) {
    $destination = Join-Path $cacheRoot $Pin.name
    if (Matches-Pin $destination $Pin) { Write-Host "Verified cached $($Pin.name)"; return $destination }
    if ($VerifyOnly) { throw "Missing or invalid download: $($Pin.name). Run normally to repair the local runtime." }
    Preserve-Invalid $destination
    $partial = $destination + '.partial'
    if (Matches-Pin $partial $Pin) { Move-Item -LiteralPath $partial -Destination $destination; return $destination }
    if ((Test-Path -LiteralPath $partial) -and (Get-Item -LiteralPath $partial).Length -ge [long]$Pin.bytes) { Preserve-Invalid $partial }
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $response = $null; $inputStream = $null; $outputStream = $null
        try {
            if ((Test-Path -LiteralPath $partial) -and (Get-Item -LiteralPath $partial).Length -ge [long]$Pin.bytes) { Preserve-Invalid $partial }
            $offset = 0L
            if (Test-Path -LiteralPath $partial) { $offset = (Get-Item -LiteralPath $partial).Length }
            Write-Host "Downloading $($Pin.name) (attempt $attempt; resume at $offset bytes)..."
            $request = [Net.HttpWebRequest]::Create($Pin.url)
            $request.UserAgent = 'CampusCenter-R28-verified-setup'
            $request.Timeout = 60000; $request.ReadWriteTimeout = 120000
            if ($offset -gt 0) { $request.AddRange($offset) }
            $response = $request.GetResponse()
            $mode = [IO.FileMode]::Create
            if ($offset -gt 0 -and [int]$response.StatusCode -eq 206) {
                if ($response.Headers['Content-Range'] -notmatch ('^bytes ' + $offset + '-\d+/' + $Pin.bytes + '$')) { throw 'Unexpected download range response.' }
                $mode = [IO.FileMode]::Append
            } elseif ([int]$response.StatusCode -eq 200) { $offset = 0L }
            else { throw "Unexpected HTTP status $($response.StatusCode)" }
            $inputStream = $response.GetResponseStream()
            $outputStream = [IO.File]::Open($partial, $mode, [IO.FileAccess]::Write, [IO.FileShare]::None)
            $buffer = New-Object byte[] (1024 * 1024)
            $total = $offset
            $nextProgress = $total + 64MB
            while (($count = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                $total += $count
                if ($total -gt [long]$Pin.bytes) { throw 'Download exceeded its pinned size.' }
                $outputStream.Write($buffer, 0, $count)
                if ($total -ge $nextProgress) { Write-Host "$($Pin.name): $total / $($Pin.bytes) bytes"; $nextProgress = $total + 64MB }
            }
            $outputStream.Dispose(); $outputStream = $null
            if (-not (Matches-Pin $partial $Pin)) { throw "SHA-256 or size mismatch: $($Pin.name)" }
            Move-Item -LiteralPath $partial -Destination $destination
            Write-Host "Downloaded and verified $($Pin.name)"
            return $destination
        } catch {
            Write-Warning $_.Exception.Message
            if ($attempt -eq 3) { throw "Could not verify $($Pin.name). Rerun to resume; no incomplete game will launch." }
        } finally {
            if ($null -ne $outputStream) { $outputStream.Dispose() }
            if ($null -ne $inputStream) { $inputStream.Dispose() }
            if ($null -ne $response) { $response.Dispose() }
        }
    }
}
function Runtime-Matches([string]$Root, $Manifest) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $false }
    foreach ($file in $Manifest) {
        if (-not (Matches-Pin (Join-Path $Root $file.path) $file)) { return $false }
    }
    $expected = @{}
    foreach ($file in $Manifest) { $expected[$file.path] = $true }
    $prefixLength = [IO.Path]::GetFullPath($Root).TrimEnd('\').Length + 1
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -Recurse -File)) {
        $relative = $file.FullName.Substring($prefixLength).Replace('\', '/')
        # Unreal may create local saves/config/logs during a normal launch.
        if (-not $expected.ContainsKey($relative) -and $relative -notmatch '^Windows/(CampusCenter|Engine)/Saved/') { return $false }
    }
    return $true
}
try {
    New-Item -ItemType Directory -Path $cacheRoot -Force | Out-Null
    $lock = [IO.File]::Open((Join-Path $buildRoot 'setup.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    # Preserve/reuse downloads from the initial bootstrap rather than fetching again.
    if ((Test-Path -LiteralPath (Join-Path $legacyRoot 'downloads')) -and @(Get-ChildItem -LiteralPath $cacheRoot -Force).Count -eq 0) {
        foreach ($old in @(Get-ChildItem -LiteralPath (Join-Path $legacyRoot 'downloads') -File)) {
            Move-Item -LiteralPath $old.FullName -Destination (Join-Path $cacheRoot $old.Name)
        }
    }
    if ((Test-Path -LiteralPath (Join-Path $legacyRoot 'expanded')) -and -not (Test-Path -LiteralPath $expanded)) {
        Move-Item -LiteralPath (Join-Path $legacyRoot 'expanded') -Destination $expanded
    }
    $manifestPath = Get-Pinned $spec.manifest
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $binaryRoot = Join-Path $expanded 'Windows\CampusCenter\Binaries\Win64'
    foreach ($file in $manifest) {
        if ($file.path -like 'Windows/*.dll') {
            $rawDllPath = $binaryRoot + '\..\..\..\' + $file.path.Substring(8).Replace('/', '\')
            if ($rawDllPath.Length -ge 260) { throw 'This checkout path is too long for the Unreal DLL loader. Move the whole CampusCenter checkout to a shorter folder (for example C:\GitHub\CampusCenter), then rerun this launcher. No Windows security or long-path settings need to change.' }
        }
    }
    if (-not (Runtime-Matches $expanded $manifest)) {
        if ($VerifyOnly) { throw 'The extracted runtime is missing or invalid. Run normally to repair it.' }
        $parts = @($spec.parts | ForEach-Object { Get-Pinned $_ })
        $archive = Join-Path $cacheRoot $spec.archive.name
        if (-not (Matches-Pin $archive $spec.archive)) {
            Preserve-Invalid $archive
            $joining = $archive + '.partial'
            $joinedStream = [IO.File]::Create($joining)
            try {
                foreach ($part in $parts) {
                    $partStream = [IO.File]::OpenRead($part)
                    try { $partStream.CopyTo($joinedStream) } finally { $partStream.Dispose() }
                }
            } finally { $joinedStream.Dispose() }
            if (-not (Matches-Pin $joining $spec.archive)) { throw 'Joined archive hash mismatch; extraction and launch stopped.' }
            Move-Item -LiteralPath $joining -Destination $archive
        }
        Write-Host 'Archive verified. Extracting and verifying all game files...'
        New-Item -ItemType Directory -Path $staging -Force | Out-Null
        $zip = [IO.Compression.ZipFile]::OpenRead($archive)
        try {
            $expected = @{}
            foreach ($file in $manifest) { $expected.Add($file.path, $file) }
            if ($zip.Entries.Count -ne $expected.Count) { throw 'Archive entry count differs from the runtime manifest.' }
            $prefix = [IO.Path]::GetFullPath($staging).TrimEnd('\') + '\'
            $seen = @{}
            foreach ($entry in $zip.Entries) {
                if (-not $expected.ContainsKey($entry.FullName) -or $seen.ContainsKey($entry.FullName)) { throw "Unexpected or duplicate archive entry: $($entry.FullName)" }
                $seen.Add($entry.FullName, $true)
                $target = [IO.Path]::GetFullPath((Join-Path $staging $entry.FullName))
                if (-not $target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe archive path.' }
                if (Matches-Pin $target $expected[$entry.FullName]) { continue }
                Preserve-Invalid $target
                New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
                $entryStream = $entry.Open(); $fileStream = [IO.File]::Create($target)
                try { $entryStream.CopyTo($fileStream) } finally { $entryStream.Dispose(); $fileStream.Dispose() }
                if (-not (Matches-Pin $target $expected[$entry.FullName])) { throw "Extracted file hash mismatch: $($entry.FullName)" }
            }
        } finally { $zip.Dispose() }
        if (-not (Runtime-Matches $staging $manifest)) { throw 'Runtime verification failed; launch stopped.' }
        Preserve-Invalid $expanded
        Move-Item -LiteralPath $staging -Destination $expanded
    }
    $executable = Join-Path $expanded $spec.executable
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) { throw "Verified executable missing: $executable" }
    Write-Host "Verified $Build R28 runtime: $executable"
    if ($PrepareOnly -or $VerifyOnly) { Write-Host 'Preparation/verification complete; game not launched.'; exit 0 }
    if ($Build -eq 'Vive') { Write-Host 'Use SteamVR as your active OpenXR runtime and connect the headset/controllers. This script does not change runtime or security settings.' }
    $start = @{ FilePath = $executable; WorkingDirectory = (Join-Path $expanded 'Windows') }
    if ($spec.arguments.Count -gt 0) { $start.ArgumentList = @($spec.arguments) }
    $launched = Start-Process @start -PassThru
    if ($launched.WaitForExit(3000) -and $launched.ExitCode -ne 0) { throw "CampusCenter exited during startup (code $($launched.ExitCode)). Check the game window or its Saved/Logs folder; no runtime/security settings were changed." }
    Write-Host 'CampusCenter started.'
} catch {
    Write-Error -ErrorAction Continue $_.Exception.Message
    exit 1
} finally { if ($null -ne $lock) { $lock.Dispose() } }
