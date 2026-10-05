# Uses the verified downloader's Hash-File, Matches-Pin and Get-Pinned functions.
$gripPins = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'CampusCenter-GripTurnR01-downloads.json') -Raw | ConvertFrom-Json
$gripRoot = Join-Path $buildRoot 'g'
$gripPayloadRoot = Join-Path $buildRoot 'gp'
$gripModePath = Join-Path $buildRoot 'grip-mode.txt'

function Get-GripPayload {
    $archive = Get-Pinned $gripPins.patch
    $good = Test-Path -LiteralPath $gripPayloadRoot -PathType Container
    foreach ($entry in $gripPins.entries) {
        if (-not (Matches-Pin (Join-Path $gripPayloadRoot $entry.path) $entry)) { $good = $false; break }
    }
    if ($good) {
        $knownPayload = @{}; foreach ($entry in $gripPins.entries) { $knownPayload[$entry.path] = $true }
        $payloadPrefix = [IO.Path]::GetFullPath($gripPayloadRoot).TrimEnd('\').Length + 1
        foreach ($file in @(Get-ChildItem -LiteralPath $gripPayloadRoot -Recurse -File)) {
            if (-not $knownPayload.ContainsKey($file.FullName.Substring($payloadPrefix).Replace('\', '/'))) { $good = $false; break }
        }
    }
    if ($good) { return }
    if ($VerifyOnly) { throw 'Grip installer cache is missing or invalid. Run normally to prepare it.' }
    if (Test-Path -LiteralPath $gripPayloadRoot) { throw 'Grip installer cache was modified; preserve it for review. No installer will run.' }
    $payloadStage = $gripPayloadRoot + '.partial'
    if (Test-Path -LiteralPath $payloadStage) { Preserve-Invalid $payloadStage }
    New-Item -ItemType Directory -Path $payloadStage | Out-Null
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        $expected = @{}; foreach ($e in $gripPins.entries) { $expected.Add($e.path, $e) }
        if ($zip.Entries.Count -ne $expected.Count) { throw 'Unexpected grip ZIP entry count.' }
        $prefix = [IO.Path]::GetFullPath($payloadStage).TrimEnd('\') + '\'; $seen = @{}
        foreach ($entry in $zip.Entries) {
            if (-not $expected.ContainsKey($entry.FullName) -or $seen.ContainsKey($entry.FullName)) { throw 'Unexpected grip ZIP entry.' }
            $seen.Add($entry.FullName, $true)
            $target = [IO.Path]::GetFullPath((Join-Path $payloadStage $entry.FullName))
            if (-not $target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe grip ZIP path.' }
            New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
            $gripInput = $entry.Open(); $gripOutput = [IO.File]::Create($target)
            try { $gripInput.CopyTo($gripOutput) } finally { $gripInput.Dispose(); $gripOutput.Dispose() }
            if (-not (Matches-Pin $target $expected[$entry.FullName])) { throw 'Grip payload hash mismatch.' }
        }
    } finally { $zip.Dispose() }
    Move-Item -LiteralPath $payloadStage -Destination $gripPayloadRoot
}

function Grip-ExpectedFiles($Manifest, [string]$Mode) {
    $expected = @{}
    foreach ($file in $Manifest) { $expected[$file.path] = $file }
    if ($Mode -eq 'patched') {
        $expected[$gripPins.native_patched.path] = $gripPins.native_patched
        foreach ($e in $gripPins.overlays) { $expected[$e.path] = $e }
    }
    return $expected
}

function Grip-KnownExtras([string]$Root, $Expected, [switch]$AllowPayload) {
    $prefixLength = [IO.Path]::GetFullPath($Root).TrimEnd('\').Length + 1
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -Recurse -File)) {
        $relative = $file.FullName.Substring($prefixLength).Replace('\', '/')
        if ($Expected.ContainsKey($relative) -or $relative -match '^Windows/(CampusCenter|Engine)/Saved/') { continue }
        $allowed = $false
        if ($AllowPayload) {
            foreach ($entry in $gripPins.entries) {
                if ($relative -eq ('Windows/' + $entry.path) -and (Matches-Pin $file.FullName $entry)) { $allowed = $true; break }
            }
            foreach ($entry in $gripPins.optional_files) {
                if ($relative -eq ('Windows/' + $entry.name) -and (Matches-Pin $file.FullName $entry)) { $allowed = $true; break }
            }
        }
        $backup = 'Windows/_GripTurnR01_Rollback/'
        if ($relative -eq ($backup + 'variant.txt')) {
            $allowed = ((Get-Content -LiteralPath $file.FullName -Raw) -eq 'R29')
        } elseif ($relative -eq ($backup + 'CampusCenter.original.exe')) {
            $allowed = Matches-Pin $file.FullName $gripPins.native_original
        } elseif ($relative -eq ($backup + 'CampusCenter.retired-grip.exe')) {
            $allowed = Matches-Pin $file.FullName $gripPins.native_patched
        } else {
            foreach ($entry in $gripPins.overlays) {
                if ($relative -eq ($backup + [IO.Path]::GetFileName($entry.path))) { $allowed = Matches-Pin $file.FullName $entry; break }
            }
        }
        if (-not $allowed) { return $false }
    }
    return $true
}

function Test-GripRuntime([string]$Root, $Manifest, [string]$Mode, [switch]$AllowPayload) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $false }
    $expected = Grip-ExpectedFiles $Manifest $Mode
    foreach ($file in $expected.Values) { if (-not (Matches-Pin (Join-Path $Root $file.path) $file)) { return $false } }
    if (-not (Grip-KnownExtras $Root $expected -AllowPayload:$AllowPayload)) { return $false }
    if ($Mode -eq 'patched' -and -not (Matches-Pin (Join-Path $Root 'Windows/_GripTurnR01_Rollback/CampusCenter.original.exe') $gripPins.native_original)) { return $false }
    return $true
}

function Invoke-GripInstaller([string]$Mode, [string]$Root) {
    if (@(Get-Process CampusCenter -ErrorAction SilentlyContinue).Count -gt 0) { throw 'Close CampusCenter before installing or rolling back the grip patch. No process was stopped.' }
    $messages = & (Join-Path $gripPayloadRoot 'InstallGripTurnPatch.exe') $Mode (Join-Path $Root 'Windows') 2>&1
    $code = $LASTEXITCODE
    foreach ($message in $messages) { Write-Host $message }
    if ($code -ne 0) { throw "Grip installer stopped (exit $code). Preserve the cache and rollback folders for review." }
}

function Get-ManagedGripRuntime([string]$BaseRoot, $Manifest) {
    Get-GripPayload
    $mode = 'patched'
    if (Test-Path -LiteralPath $gripModePath) {
        $mode = (Get-Content -LiteralPath $gripModePath -Raw).Trim()
        if ($mode -notin @('patched', 'original')) { throw 'Invalid saved grip mode. Preserve it for review.' }
    }
    if ($RollbackGripPatch) { $mode = 'original' }
    if ($EnableGripPatch) { $mode = 'patched' }
    $isPatched = Test-GripRuntime $gripRoot $Manifest 'patched'
    $isOriginal = $false
    if (-not $isPatched) { $isOriginal = Test-GripRuntime $gripRoot $Manifest 'original' }
    if ((Test-Path -LiteralPath $gripRoot) -and -not ($isPatched -or $isOriginal)) { throw 'Managed Vive runtime has unknown or altered files. It was preserved; no update or game launch will run.' }
    # Respect a valid manual rollback instead of silently re-enabling it.
    if ($isOriginal -and -not $EnableGripPatch) { $mode = 'original' }
    if ($VerifyOnly) {
        if (($mode -eq 'patched' -and -not $isPatched) -or ($mode -eq 'original' -and -not $isOriginal)) { throw 'Managed grip runtime is not prepared for its selected mode. Run normally to prepare it.' }
        Write-Host "Verified grip mode: $mode"
        return $gripRoot
    }
    if ($isPatched -and $mode -eq 'original') {
        Invoke-GripInstaller 'rollback' $gripRoot
        if (-not (Test-GripRuntime $gripRoot $Manifest 'original')) { throw 'Grip rollback verification failed.' }
        $isOriginal = $true; $isPatched = $false
    }
    if (($mode -eq 'patched' -and -not $isPatched) -or ($mode -eq 'original' -and -not $isOriginal)) {
        $stage = $gripRoot + '.partial'
        if (Test-Path -LiteralPath $stage) { Preserve-Invalid $stage }
        New-Item -ItemType Directory -Path $stage | Out-Null
        $baseNative = Join-Path $BaseRoot $gripPins.native_original.path
        $originalNative = $baseNative
        if (Matches-Pin $baseNative $gripPins.native_patched) { $originalNative = Join-Path $BaseRoot 'Windows/_GripTurnR01_Rollback/CampusCenter.original.exe' }
        if (-not (Matches-Pin $originalNative $gripPins.native_original)) { throw 'Verified original native executable is unavailable; no patch applied.' }
        foreach ($file in $Manifest) {
            $source = Join-Path $BaseRoot $file.path
            if ($file.path -eq $gripPins.native_original.path) { $source = $originalNative }
            if (-not (Matches-Pin $source $file)) { throw "Base source changed during copy: $($file.path)" }
            $destination = Join-Path $stage $file.path
            New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $destination
        }
        $savedSource = $BaseRoot
        if (Test-Path -LiteralPath $gripRoot) { $savedSource = $gripRoot }
        foreach ($relative in @('Windows/CampusCenter/Saved', 'Windows/Engine/Saved')) {
            $source = Join-Path $savedSource $relative
            if (Test-Path -LiteralPath $source) { Copy-Item -LiteralPath $source -Destination (Join-Path $stage $relative) -Recurse }
        }
        if ($mode -eq 'patched') { Invoke-GripInstaller 'install' $stage }
        if (-not (Test-GripRuntime $stage $Manifest $mode)) { throw 'Managed grip runtime verification failed. Staging and original files were preserved.' }
        if (Test-Path -LiteralPath $gripRoot) { Preserve-Invalid $gripRoot }
        Move-Item -LiteralPath $stage -Destination $gripRoot
    }
    [IO.File]::WriteAllText($gripModePath, $mode)
    Write-Host "Verified grip mode: $mode. Pristine/manual base cache preserved."
    return $gripRoot
}
