# Word page count + PDF export for the two IEIE submissions (run natively; needs MS Word).
# Usage (repo root): powershell -ExecutionPolicy Bypass -File src\paper\paper_pagecount.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$out = Join-Path $root "docs\paper\_check"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $true   # visible: any blocking dialog (font, repair, protected view) is shown to the user
$word.DisplayAlerts = 0
$lines = @()
foreach ($name in @("ieie2026f_proceedings_final", "ieie2026f_blind_final")) {
    $path = Join-Path $root "docs\paper\$name.docx"
    $doc = $word.Documents.Open($path, $false, $true, $false)   # ConfirmConversions=false, ReadOnly=true, AddToRecent=false
    $doc.Repaginate()
    $pages = $doc.ComputeStatistics(2)
    $pdf = Join-Path $out "$name.pdf"
    $doc.ExportAsFixedFormat($pdf, 17)
    $doc.Saved = $true
    $doc.Close([ref]0)   # 0 = wdDoNotSaveChanges
    $lines += "$name pages=$pages"
    Write-Host "$name pages=$pages"
}
$word.Quit()
$lines | Out-File -FilePath (Join-Path $out "pagecount.txt") -Encoding ascii
$lines
