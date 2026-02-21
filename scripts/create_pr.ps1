param(
  [string]$Branch = "hybrid/soffice-hybrid-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
  [string]$Remote = 'origin',
  [string]$Base = 'main'
)

Write-Host "Creating branch: $Branch"
# Locate git: prefer system `git` if available, otherwise fall back to common install locations
$GitExe = $null
if (Get-Command git -ErrorAction SilentlyContinue) {
  $GitExe = 'git'
} else {
  $candidates = @( 
    "C:\\Program Files\\Git\\cmd\\git.exe",
    "C:\\Program Files (x86)\\Git\\cmd\\git.exe",
    "C:\\Program Files\\Git\\bin\\git.exe"
  )
  foreach ($p in $candidates) {
    if (Test-Path $p) { $GitExe = $p; break }
  }
}

if (-not $GitExe) {
  Write-Host "Error: 'git' is not available in PATH and no common Git install locations were found."
  Write-Host "Please install Git for Windows and ensure it's on your PATH."
  Write-Host "Install via: https://git-scm.com/download/win or using winget: winget install --id Git.Git -e"
  exit 1
}

Write-Host "Using git executable: $GitExe"
& $GitExe fetch $Remote
& $GitExe checkout -b $Branch

Write-Host "Staging changes..."
& $GitExe add -A

Write-Host "Committing..."
$msg1 = 'feat(hybrid): prefer LibreOffice UNO daemon with CLI fallback'
$msg2 = 'Includes: services/document_conversion.py, docs, tests, deployment configs'
try {
  & $GitExe commit -m $msg1 -m $msg2
} catch {
  Write-Host "No changes to commit or commit failed: $_"
}

Write-Host "Pushing to $Remote/$Branch"
& $GitExe push -u $Remote $Branch

# Locate gh (GitHub CLI)
$GhExe = $null
if (Get-Command gh -ErrorAction SilentlyContinue) {
  $GhExe = 'gh'
} else {
  $ghCandidates = @(
    "$env:ProgramFiles\GitHub CLI\gh.exe",
    "$env:ProgramFiles(x86)\GitHub CLI\gh.exe",
    "$env:USERPROFILE\scoop\apps\gh\current\bin\gh.exe",
    "C:\\Program Files\\Git\\cmd\\gh.exe",
    "C:\\Program Files\\Git\\bin\\gh.exe"
  )
  foreach ($p in $ghCandidates) { if (Test-Path $p) { $GhExe = $p; break } }
}

if ($GhExe) {
  Write-Host "Using gh executable: $GhExe"
  # Check authentication status
  $authOk = $false
  try {
    $status = & $GhExe auth status 2>&1
    if ($LASTEXITCODE -eq 0 -or $status -match 'Logged in') { $authOk = $true }
  } catch {
    $authOk = $false
  }

  if (-not $authOk) {
    Write-Host "gh not authenticated. Running interactive login (follow prompts)..."
    & $GhExe auth login
    # re-check
    try { $status = & $GhExe auth status 2>&1; if ($LASTEXITCODE -eq 0 -or $status -match 'Logged in') { $authOk = $true } } catch {}
  }

  if ($authOk) {
    Write-Host "Creating PR via gh..."
    $bodyFile = Join-Path $PSScriptRoot 'PR_BODY.txt'
    if (Test-Path $bodyFile) {
      & $GhExe pr create --base $Base --head $Branch --title "Hybrid: LibreOffice UNO daemon + CLI fallback" --body-file $bodyFile
    } else {
      & $GhExe pr create --base $Base --head $Branch --title "Hybrid: LibreOffice UNO daemon + CLI fallback" --body "Implements hybrid UNO daemon + CLI fallback, adds docs, tests, and deployment configs."
    }
  } else {
    Write-Host "gh authentication failed or canceled. You can run: $GhExe auth login" 
  }
} else {
  Write-Host "gh CLI not found. To open a PR manually run:"
  Write-Host "  gh pr create --base $Base --head $Branch --title 'Hybrid: LibreOffice UNO daemon + CLI fallback' --body '...'"
}

Write-Host 'Done.'
