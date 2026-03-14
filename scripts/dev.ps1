param(
    [ValidateSet("backend", "frontend", "all", "test")]
    [string]$Target = "all"
)

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Ensure-FrontendDeps {
    Push-Location (Join-Path $Root "frontend")
    try {
        if (-not (Test-Path "node_modules")) {
            npm ci
        }
    }
    finally {
        Pop-Location
    }
}

switch ($Target) {
    "backend" {
        Set-Location (Join-Path $Root "backend")
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        break
    }
    "frontend" {
        Ensure-FrontendDeps
        Set-Location (Join-Path $Root "frontend")
        npm run dev -- --host 0.0.0.0 --port 5173
        break
    }
    "test" {
        Set-Location $Root
        python -m pip install -r backend/requirements.txt pytest
        pytest -q
        break
    }
    "all" {
        $backendCommand = "Set-Location '$($Root.Replace("'", "''"))\\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

        Ensure-FrontendDeps
        Set-Location (Join-Path $Root "frontend")
        npm run dev -- --host 0.0.0.0 --port 5173
        break
    }
}
