param(
    [string]$TargetDirectory = (Join-Path $HOME '.agents\skills'),
    [string]$RepositoryUrl = 'https://github.com/Todd-Caron_Taylor/CodePulse.git'
)

$ErrorActionPreference = 'Stop'

$target = [System.IO.Path]::GetFullPath($TargetDirectory)
$staging = Join-Path ([System.IO.Path]::GetTempPath()) ('CodePulse-' + [guid]::NewGuid())

try {
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    git clone --depth 1 $RepositoryUrl $staging

    if ($LASTEXITCODE -ne 0) {
        throw 'CodePulse clone failed.'
    }

    Get-ChildItem -LiteralPath $staging -Directory -Force |
        Where-Object { $_.Name -ne '.git' } |
        Copy-Item -Destination $target -Recurse -Force

    Write-Host "CodePulse installed to $target"
}
finally {
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}