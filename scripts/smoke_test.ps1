param(
  [switch]$StartStack = $true,
  [string]$ProjectRoot = "D:\testing-life-signify\life-sinify-saas-product-v2"
)

$ErrorActionPreference = "Stop"

$composeFile = Join-Path $ProjectRoot "docker-compose.yml"
$results = New-Object System.Collections.Generic.List[object]
$criticalFailed = 0

function Add-Result {
  param(
    [string]$Check,
    [bool]$Ok,
    [string]$Detail,
    [switch]$Critical
  )

  if ($Critical -and -not $Ok) { $script:criticalFailed++ }
  $results.Add([pscustomobject]@{
      Check  = $Check
      Status = if ($Ok) { "PASS" } else { "FAIL" }
      Detail = $Detail
    }) | Out-Null
}

function Get-StatusCode {
  param([string]$Url)
  try {
    return (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 25).StatusCode
  } catch {
    if ($_.Exception.Response) {
      return [int]$_.Exception.Response.StatusCode.value__
    }
    throw
  }
}

Write-Host "Running smoke tests from: $ProjectRoot" -ForegroundColor Cyan

if ($StartStack) {
  try {
    docker compose -f $composeFile up -d | Out-Null
    Add-Result -Check "Compose up" -Ok $true -Detail "Stack is up" -Critical
  } catch {
    Add-Result -Check "Compose up" -Ok $false -Detail $_.Exception.Message -Critical
  }
}

try {
  $psOut = docker compose -f $composeFile ps
  Add-Result -Check "Compose ps" -Ok $true -Detail (($psOut -join "`n").Substring(0, [Math]::Min(240, ($psOut -join "`n").Length)))
} catch {
  Add-Result -Check "Compose ps" -Ok $false -Detail $_.Exception.Message -Critical
}

# Backend health/root
try {
  $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 25
  Add-Result -Check "Backend /health" -Ok $true -Detail ($health | ConvertTo-Json -Compress) -Critical
} catch {
  Add-Result -Check "Backend /health" -Ok $false -Detail $_.Exception.Message -Critical
}

try {
  $root = Invoke-RestMethod -Uri "http://localhost:8000/" -TimeoutSec 25
  Add-Result -Check "Backend /" -Ok $true -Detail ($root | ConvertTo-Json -Compress) -Critical
} catch {
  Add-Result -Check "Backend /" -Ok $false -Detail $_.Exception.Message -Critical
}

# Frontend route reachability
$frontendRoutes = @(
  "/",
  "/login",
  "/register",
  "/dashboard",
  "/reports",
  "/generate-report",
  "/billing",
  "/settings",
  "/admin",
  "/admin/users"
)

foreach ($route in $frontendRoutes) {
  try {
    $code = Get-StatusCode -Url ("http://localhost:5173" + $route)
    Add-Result -Check ("Frontend " + $route) -Ok ($code -eq 200) -Detail ("HTTP " + $code) -Critical
  } catch {
    Add-Result -Check ("Frontend " + $route) -Ok $false -Detail $_.Exception.Message -Critical
  }
}

# Register/login and service checks
$email = "smoke" + (Get-Random) + "@example.com"
$org = "Smoke Org " + (Get-Random)
$password = "Password123"
$token = $null

try {
  $registerBody = @{
    full_name         = "Smoke User"
    mobile_no         = "9999999999"
    country           = "India"
    state             = "Maharashtra"
    email             = $email
    organization_name = $org
    password          = $password
    payment_method    = "UPI"
  } | ConvertTo-Json

  $reg = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/users/register" -ContentType "application/json" -Body $registerBody -TimeoutSec 30
  Add-Result -Check "API register" -Ok $true -Detail ("user_id=" + $reg.id + ", email=" + $reg.email) -Critical
} catch {
  Add-Result -Check "API register" -Ok $false -Detail $_.Exception.Message -Critical
}

try {
  $form = "username=$([uri]::EscapeDataString($email))&password=$([uri]::EscapeDataString($password))"
  $login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/users/login" -ContentType "application/x-www-form-urlencoded" -Body $form -TimeoutSec 30
  $token = $login.access_token
  Add-Result -Check "API login" -Ok (-not [string]::IsNullOrWhiteSpace($token)) -Detail "Token received" -Critical
} catch {
  Add-Result -Check "API login" -Ok $false -Detail $_.Exception.Message -Critical
}

if ($token) {
  $authHeader = @{ Authorization = "Bearer $token" }

  try {
    $me = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/users/me" -Headers $authHeader -TimeoutSec 30
    $hasFields = (-not [string]::IsNullOrWhiteSpace($me.full_name)) -and
      (-not [string]::IsNullOrWhiteSpace($me.mobile_no)) -and
      (-not [string]::IsNullOrWhiteSpace($me.country)) -and
      (-not [string]::IsNullOrWhiteSpace($me.state))
    Add-Result -Check "API users/me fields" -Ok $hasFields -Detail ("name=" + $me.full_name + ", mobile=" + $me.mobile_no + ", country=" + $me.country + ", state=" + $me.state) -Critical
  } catch {
    Add-Result -Check "API users/me fields" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $usage = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/reports/metrics/usage" -Headers $authHeader -TimeoutSec 30
    Add-Result -Check "API reports usage" -Ok $true -Detail ($usage | ConvertTo-Json -Compress) -Critical
  } catch {
    Add-Result -Check "API reports usage" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $reports = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/reports/" -Headers $authHeader -TimeoutSec 30
    Add-Result -Check "API reports list" -Ok $true -Detail ("count=" + @($reports).Count)
  } catch {
    Add-Result -Check "API reports list" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $plans = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/payments/plans" -Headers $authHeader -TimeoutSec 30
    Add-Result -Check "API payments plans" -Ok $true -Detail ("count=" + @($plans).Count)
  } catch {
    Add-Result -Check "API payments plans" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $history = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/payments/history" -Headers $authHeader -TimeoutSec 30
    Add-Result -Check "API payments history" -Ok $true -Detail ("count=" + @($history).Count)
  } catch {
    Add-Result -Check "API payments history" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $orgUsers = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/users/org-users" -Headers $authHeader -TimeoutSec 30
    Add-Result -Check "API org users" -Ok $true -Detail ("count=" + @($orgUsers).Count)
  } catch {
    Add-Result -Check "API org users" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $inviteBody = @{ email = ("invite" + (Get-Random) + "@example.com"); role = "user" } | ConvertTo-Json
    $invite = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/users/invite" -Headers $authHeader -ContentType "application/json" -Body $inviteBody -TimeoutSec 30
    Add-Result -Check "API invite user" -Ok $true -Detail $invite.message
  } catch {
    Add-Result -Check "API invite user" -Ok $false -Detail $_.Exception.Message -Critical
  }

  try {
    $code = Get-StatusCode -Url "http://localhost:8000/api/admin/analytics"
    Add-Result -Check "API admin analytics (admin role)" -Ok ($code -eq 403) -Detail ("HTTP " + $code + ", expected 403")
  } catch {
    Add-Result -Check "API admin analytics (admin role)" -Ok $false -Detail $_.Exception.Message
  }

  try {
    $proxyMe = Invoke-WebRequest -Method Get -Uri "http://localhost:5173/api/users/me" -Headers $authHeader -UseBasicParsing -TimeoutSec 30
    Add-Result -Check "Frontend proxy /api/users/me" -Ok ($proxyMe.StatusCode -eq 200) -Detail ("HTTP " + $proxyMe.StatusCode) -Critical
  } catch {
    Add-Result -Check "Frontend proxy /api/users/me" -Ok $false -Detail $_.Exception.Message -Critical
  }

  # Optional check: can fail if Razorpay test setup is not configured.
  try {
    $orderBody = @{ plan = "pro" } | ConvertTo-Json
    $order = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/payments/create-order" -Headers $authHeader -ContentType "application/json" -Body $orderBody -TimeoutSec 35
    Add-Result -Check "API create-order (optional)" -Ok $true -Detail ("order_id=" + $order.id)
  } catch {
    Add-Result -Check "API create-order (optional)" -Ok $false -Detail "Optional check failed (likely Razorpay config)." 
  }
}

$results | Format-Table -AutoSize | Out-String -Width 260 | Write-Host

if ($criticalFailed -gt 0) {
  Write-Host ""
  Write-Host "Smoke test FAILED: $criticalFailed critical checks failed." -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "Smoke test PASSED: all critical checks passed." -ForegroundColor Green
exit 0
