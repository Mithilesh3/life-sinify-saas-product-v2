param(
  [switch]$WhatIfOnly = $false
)

$paths = @(
  "D:\testing-life-signify\life-sinify-saas-product-v2\dist",
  "D:\testing-life-signify\life-sinify-saas-product-v2\.vite",
  "D:\testing-life-signify\life-sinify-saas-product-v2\node_modules",
  "D:\testing-life-signify\life-sinify-saas-product-v2\frontend\dist",
  "D:\testing-life-signify\life-sinify-saas-product-v2\src"
)

Write-Host "Cleanup target list:" -ForegroundColor Cyan
foreach ($path in $paths) {
  if (Test-Path $path) {
    Write-Host "  FOUND: $path" -ForegroundColor Yellow
  } else {
    Write-Host "  MISSING: $path" -ForegroundColor DarkGray
  }
}

if ($WhatIfOnly) {
  Write-Host ""
  Write-Host "Preview mode only. No files were deleted." -ForegroundColor Green
  exit 0
}

Write-Host ""
Write-Host "Deleting found paths..." -ForegroundColor Cyan
foreach ($path in $paths) {
  if (Test-Path $path) {
    Remove-Item -Recurse -Force $path
    Write-Host "  DELETED: $path" -ForegroundColor Green
  }
}

Write-Host ""
Write-Host "Cleanup completed." -ForegroundColor Green
