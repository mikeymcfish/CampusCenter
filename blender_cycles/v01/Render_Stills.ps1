$ErrorActionPreference='Stop'
$blender='C:/Program Files/Blender Foundation/Blender 5.0/blender.exe'
$scene=Join-Path $PSScriptRoot 'Campus_Center_Cycles_Studio.blend'
$script=Join-Path $PSScriptRoot 'render_stills.py'
& $blender --factory-startup -b $scene --python $script
if($LASTEXITCODE -ne 0){throw 'Blender render failed. Inspect the console output.'}
