# deploy-web.ps1 - one-click sync web/ to gh-pages and push (GitHub Pages deploy)
# Usage: cd D:\VS CODE\PROJECT\hanwebgame ; .\deploy-web.ps1
$repo = $PSScriptRoot
$tmp  = Join-Path $env:TEMP 'hanweb_ghpages_deploy'

Write-Host "repo: $repo"

$web = Join-Path $repo 'web'
if (-not (Test-Path $web)) { throw 'web/ folder not found' }

if (Test-Path $tmp) { git -C $repo worktree remove --force $tmp 2>$null | Out-Null }

git -C $repo fetch origin gh-pages 2>$null
if ($LASTEXITCODE -ne 0) { throw 'fetch failed' }
git -C $repo worktree add $tmp gh-pages 2>$null
if ($LASTEXITCODE -ne 0) { throw 'worktree add failed' }

try {
    Get-ChildItem -Force $tmp | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force
    Copy-Item -Recurse -Force (Join-Path $web '*') $tmp

    git -C $tmp add -A
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    git -C $tmp -c user.name='wahaha232' -c user.email='wahaha232@gmail.com' commit -m ('web update ' + $stamp) 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'commit failed (nothing to commit?)' }
    git -C $tmp push origin gh-pages 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'push failed' }
    Write-Host 'deployed: https://wahaha232.github.io/hanwebgame/'
}
finally {
    git -C $repo worktree remove --force $tmp 2>$null | Out-Null
}
