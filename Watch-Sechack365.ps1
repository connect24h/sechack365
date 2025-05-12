[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# ─── 設定値 ───────────────────────────────────────
$url          = 'https://sechack365.nict.go.jp/'   # 監視対象 URL
$checkDelay   = 10                               # 監視間隔（秒）
$stateFile    = "$PSScriptRoot\page_signature.txt" # 前回ヘッダー保存先
# ────────────────────────────────────────────────

function Get-PageSignature {
    param([string]$u)

    # ヘッダーだけ取れば軽量（Invoke-RestMethod でも可）
    $r = Invoke-WebRequest -Uri $u -Method Head -ErrorAction Stop
    # 代表的な更新指標をまとめて 1 行に
    return "$($r.Headers['ETag']),$($r.Headers['Last-Modified'])"
}

# 前回の値を取得（初回は空文字列）
$prev = if (Test-Path $stateFile) { Get-Content $stateFile -Raw } else { '' }

while ($true) {
    try {
        $now = Get-PageSignature $url
        if ($now -and $now -ne $prev) {
            Write-Output 'ページが更新された'
            $now | Set-Content $stateFile
            $prev = $now
        } else {
            Write-Output '更新無し'
        }
    } catch {
        Write-Warning "取得失敗: $_"
    }
    Start-Sleep -Seconds $checkDelay
}
