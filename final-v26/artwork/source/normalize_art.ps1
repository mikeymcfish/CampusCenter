Add-Type -AssemblyName System.Drawing
$artOut = Join-Path $PSScriptRoot 'art_batch_v26_r01'
New-Item -ItemType Directory -Force -Path (Join-Path $artOut 'textures') | Out-Null
$artSrc = 'C:\Users\mikef\Documents\Codex\2026-09-30\task\CampusCenter-new-plans\references\art\future_unreal_20260930'
$artReport = @{}
foreach ($artFile in Get-ChildItem -LiteralPath $artSrc -Filter '*.jpeg') {
 $artStream = [IO.File]::OpenRead($artFile.FullName)
 $artImage = [Drawing.Image]::FromStream($artStream,$true,$true)
 $artRaw = @($artImage.Width,$artImage.Height)
 $artOrientation = 1
 if ($artImage.PropertyIdList -contains 274) {$artOrientation = [BitConverter]::ToUInt16($artImage.GetPropertyItem(274).Value,0)}
 $artProfile = $artImage.PropertyIdList -contains 34675
 if ($artOrientation -eq 6) {$artImage.RotateFlip([Drawing.RotateFlipType]::Rotate90FlipNone)}
 elseif ($artOrientation -eq 3) {$artImage.RotateFlip([Drawing.RotateFlipType]::Rotate180FlipNone)}
 elseif ($artOrientation -eq 8) {$artImage.RotateFlip([Drawing.RotateFlipType]::Rotate270FlipNone)}
 $artBitmap = New-Object Drawing.Bitmap $artImage.Width,$artImage.Height
 $artGraphics = [Drawing.Graphics]::FromImage($artBitmap)
 $artGraphics.DrawImage($artImage,0,0,$artImage.Width,$artImage.Height)
 $artBitmap.Save((Join-Path $artOut ('textures\ART26_'+$artFile.BaseName+'.png')),[Drawing.Imaging.ImageFormat]::Png)
 $artReport[$artFile.Name] = @{raw_size=$artRaw;output_size=@($artImage.Width,$artImage.Height);exif_orientation=$artOrientation;icc_present=$artProfile;normalization='System.Drawing FromStream embedded color management enabled; draw to RGB bitmap; EXIF rotation baked; MPO primary RGB image only';creative_edits=$false}
 $artGraphics.Dispose();$artBitmap.Dispose();$artImage.Dispose();$artStream.Dispose()
}
$artReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $artOut 'normalization.json') -Encoding utf8
