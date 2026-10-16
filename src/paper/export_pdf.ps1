# Export both IEIE docx files to PDF with Word (read-only open, no save). Run from any folder.
$ErrorActionPreference = "Stop"
$root = "C:\Users\USER\co-deep-hb"
$out = Join-Path $root "docs\paper\_check"
New-Item -ItemType Directory -Force $out | Out-Null
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    foreach ($n in @("proceedings", "blind")) {
        $src = Join-Path $root "docs\paper\ieie2026f_${n}_final.docx"
        $pdf = Join-Path $out "ieie2026f_${n}_final.pdf"
        $doc = $w.Documents.Open($src, $false, $true, $false)
        $doc.ExportAsFixedFormat($pdf, 17)
        Write-Host ("{0}: {1} pages -> {2}" -f $n, $doc.ComputeStatistics(2), $pdf)
        $doc.Close(0)
    }
} finally {
    $w.Quit(0)
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($w)
}
