$ErrorActionPreference = 'Stop'
$downloadRoot = $PSScriptRoot
$archiveManifest = Get-Content -LiteralPath (Join-Path $downloadRoot 'ARCHIVE_MANIFEST.json') -Raw | ConvertFrom-Json
foreach ($expectedArchive in @($archiveManifest | Where-Object { $_.parts.Count -gt 0 })) {
    $archiveName = $expectedArchive.name
    $archiveParts = @(Get-ChildItem -LiteralPath $downloadRoot -File | Where-Object Name -Like "$archiveName.part*" | Sort-Object Name)
    if ($archiveParts.Count -eq 0) { continue }
    if ($archiveParts.Count -ne $expectedArchive.parts.Count) { throw "Download all $($expectedArchive.parts.Count) parts of $archiveName" }
    for ($partIndex = 0; $partIndex -lt $archiveParts.Count; $partIndex++) {
        $expectedName = "$archiveName.part{0:D2}" -f ($partIndex + 1)
        if ($archiveParts[$partIndex].Name -ne $expectedName) { throw "Missing part: $expectedName" }
    }
    $outputPath = Join-Path $downloadRoot $archiveName
    if (Test-Path -LiteralPath $outputPath) { throw "Output already exists: $outputPath" }
    $outputStream = [System.IO.File]::Create($outputPath)
    try {
        foreach ($archivePart in $archiveParts) {
            $inputStream = [System.IO.File]::OpenRead($archivePart.FullName)
            try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose() }
        }
    } finally { $outputStream.Dispose() }
    if ((Get-Item -LiteralPath $outputPath).Length -ne $expectedArchive.bytes) { throw "Size mismatch: $archiveName" }
    $hashStream = [System.IO.File]::OpenRead($outputPath)
    $hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $computedHash = ([System.BitConverter]::ToString($hashAlgorithm.ComputeHash($hashStream))).Replace('-', '').ToLowerInvariant()
    } finally {
        $hashStream.Dispose()
        $hashAlgorithm.Dispose()
    }
    if ($computedHash -ne $expectedArchive.sha256) { throw "SHA256 mismatch: $archiveName" }
    Write-Host "Verified $archiveName. Extract it completely before running its launcher."
}
