$ErrorActionPreference = 'Stop'
$launcher = Join-Path $PSScriptRoot 'Walk_Commons_Dusk.cmd'
if (-not (Test-Path -LiteralPath $launcher)) { throw 'Current Unreal walkthrough launcher is missing.' }
& $launcher
