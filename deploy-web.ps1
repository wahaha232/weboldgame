# deploy-web.ps1 — 同步 web/ 到 gh-pages 並推送(一鍵部署 GitHub Pages)
# 用法: 在 D:\VS CODE\PROJECT\hanwebgame 下執行  .\deploy-web.ps1
$ErrorActionPreference = 'Stop'
$repo = $PSScriptRoot
$tmp  = Join-Path $env:TEMP 'hanweb_ghpages_deploy'

Write-Host "repo: $repo"

# 1) 確認 web/ 存在
$web = Join-Path $repo 'web'
if (-not (Test-Path $web)) { throw '找不到 web/ 資料夾' }

# 2) 建立/重設 worktree
if (Test-Path $tmp) { git -C $repo worktree remove --force $tmp 2>$null | Out-Null }
git -C $repo fetch origin gh-pages 2>&1 | Out-Null
git -C $repo worktree add $tmp gh-pages 2>&1 | Out-Null
try {
    # 3) 清空 worktree(保留 .git)並複製最新 web 內容
    Get-ChildItem -Force $tmp | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force
    Copy-Item -Recurse -Force (Join-Path $web '*') $tmp

    # 4) commit & push
    git -C $tmp add -A
    $msg = "web update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git -C $tmp -c user.name="wahaha232" -c user.email="wahaha232@gmail.com" commit -m $msg
    git -C $tmp push origin gh-pages
    Write-Host "已部署: https://wahaha232.github.io/hanwebgame/"
}
finally {
    git -C $repo worktree remove --force $tmp 2>$null | Out-Null
}
