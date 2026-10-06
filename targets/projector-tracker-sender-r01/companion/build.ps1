param([switch]$Test)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:DOTNET_CLI_HOME = Join-Path $PSScriptRoot '.dotnet-local'
$env:NUGET_PACKAGES = Join-Path $PSScriptRoot '.nuget-local'
$env:DOTNET_GENERATE_ASPNET_CERTIFICATE = 'false'
$env:DOTNET_ADD_GLOBAL_TOOLS_TO_PATH = 'false'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
dotnet build src\Tracker.App\Tracker.App.csproj -c Release --nologo
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
if ($Test) {
  dotnet run --project tests\Tracker.Tests\Tracker.Tests.csproj -c Release -- $PSScriptRoot
  if ($LASTEXITCODE -ne 0) { throw 'QA failed' }
}
