Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseDir = Join-Path $root "base-images"
$outDir = Join-Path $root "final-slides"
$logoPath = "C:\Users\dnlfl\Devs\Zeppelin\logos\LogoPNG.png"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$navy = [System.Drawing.Color]::FromArgb(255, 8, 34, 61)
$darkNavy = [System.Drawing.Color]::FromArgb(255, 4, 22, 42)
$white = [System.Drawing.Color]::FromArgb(255, 245, 244, 242)
$gold = [System.Drawing.Color]::FromArgb(255, 185, 146, 90)
$softNavy = [System.Drawing.Color]::FromArgb(220, 8, 34, 61)

function New-Font($family, $size, $style) {
  return New-Object System.Drawing.Font($family, $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
}

function New-Brush($color) {
  return New-Object System.Drawing.SolidBrush($color)
}

function Draw-Overlay($g, $fromTop, $alpha, $height) {
  $rect = [System.Drawing.Rectangle]::new(0, $fromTop, 1080, $height)
  $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $rect,
    [System.Drawing.Color]::FromArgb(0, 0, 0, 0),
    [System.Drawing.Color]::FromArgb($alpha, 0, 0, 0),
    90
  )
  $g.FillRectangle($brush, $rect)
  $brush.Dispose()
}

function Draw-Logo($g, $mode) {
  $logo = [System.Drawing.Image]::FromFile($logoPath)
  $w = 82
  $h = [int]($w * $logo.Height / $logo.Width)
  $x = 1080 - $w - 58
  $y = 54
  $tinted = New-Object System.Drawing.Bitmap $w, $h, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $tg = [System.Drawing.Graphics]::FromImage($tinted)
  $tg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $tg.DrawImage($logo, 0, 0, $w, $h)
  $tg.Dispose()
  $target = if ($mode -eq "light") { [System.Drawing.Color]::FromArgb(95, 8, 34, 61) } else { [System.Drawing.Color]::FromArgb(115, 245, 244, 242) }
  for ($px = 0; $px -lt $tinted.Width; $px++) {
    for ($py = 0; $py -lt $tinted.Height; $py++) {
      $c = $tinted.GetPixel($px, $py)
      if ($c.A -gt 8 -and (($c.R + $c.G + $c.B) -gt 40)) {
        $tinted.SetPixel($px, $py, [System.Drawing.Color]::FromArgb([int]($target.A * ($c.A / 255.0)), $target.R, $target.G, $target.B))
      } else {
        $tinted.SetPixel($px, $py, [System.Drawing.Color]::FromArgb(0,0,0,0))
      }
    }
  }
  $g.DrawImage($tinted, $x, $y, $w, $h)
  $logo.Dispose()
  $tinted.Dispose()
}

function Draw-LineSegments($g, $segments, $x, $y, $font, $defaultBrush) {
  $cx = [float]$x
  foreach ($segment in $segments) {
    $text = $segment.Text
    $brush = if ($segment.Color -eq "gold") { New-Brush $gold } else { $defaultBrush }
    $g.DrawString($text, $font, $brush, $cx, $y)
    $size = $g.MeasureString($text, $font)
    $cx += $size.Width - 3
    if ($brush -ne $defaultBrush) { $brush.Dispose() }
  }
}

function Draw-CenteredLineSegments($g, $segments, $centerX, $y, $font, $defaultBrush) {
  $total = 0
  foreach ($segment in $segments) {
    $total += ($g.MeasureString($segment.Text, $font).Width - 3)
  }
  Draw-LineSegments $g $segments ($centerX - ($total / 2)) $y $font $defaultBrush
}

function Draw-PlainLines($g, $lines, $x, $y, $font, $brush, $lineGap) {
  $cy = [float]$y
  foreach ($line in $lines) {
    $g.DrawString($line, $font, $brush, $x, $cy)
    $cy += $font.Height + $lineGap
  }
}

function Draw-SlideNumber($g, $n, $mode) {
  $font = New-Font "Candara" 20 ([System.Drawing.FontStyle]::Bold)
  $brush = if ($mode -eq "light") { New-Brush ([System.Drawing.Color]::FromArgb(140, 8, 34, 61)) } else { New-Brush ([System.Drawing.Color]::FromArgb(165, 245, 244, 242)) }
  $goldBrush = New-Brush ([System.Drawing.Color]::FromArgb(190, 185, 146, 90))
  $g.DrawString(("{0:D2}/07" -f $n), $font, $brush, 58, 54)
  $g.FillRectangle($goldBrush, 58, 87, 46, 4)
  $font.Dispose(); $brush.Dispose(); $goldBrush.Dispose()
}

function Save-Slide($n, $drawAction) {
  $basePath = Join-Path $baseDir ("slide-{0:D2}-base.png" -f $n)
  $outPath = Join-Path $outDir ("slide-{0:D2}.png" -f $n)
  $img = [System.Drawing.Image]::FromFile($basePath)
  $bmp = New-Object System.Drawing.Bitmap 1080, 1350, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.DrawImage($img, 0, 0, 1080, 1350)
  & $drawAction $g
  $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $img.Dispose()
}

$title = New-Font "Bahnschrift" 78 ([System.Drawing.FontStyle]::Bold)
$titleBig = New-Font "Bahnschrift" 88 ([System.Drawing.FontStyle]::Bold)
$titleMid = New-Font "Bahnschrift" 64 ([System.Drawing.FontStyle]::Bold)
$body = New-Font "Candara" 42 ([System.Drawing.FontStyle]::Regular)
$bodySmall = New-Font "Candara" 34 ([System.Drawing.FontStyle]::Regular)
$bodyBold = New-Font "Candara" 46 ([System.Drawing.FontStyle]::Bold)
$whiteBrush = New-Brush $white
$navyBrush = New-Brush $navy
$goldBrush = New-Brush $gold

Save-Slide 1 {
  param($g)
  Draw-Overlay $g 420 220 930
  Draw-CenteredLineSegments $g @(@{ Text = "Seu paciente"; Color = "white" }) 540 730 $titleBig $whiteBrush
  Draw-CenteredLineSegments $g @(@{ Text = "não "; Color = "white" }, @{ Text = "faltou."; Color = "gold" }) 540 820 $titleBig $whiteBrush
  $g.FillRectangle($goldBrush, 440, 934, 200, 5)
  Draw-CenteredLineSegments $g @(@{ Text = "Ele "; Color = "white" }, @{ Text = "esqueceu"; Color = "gold" }) 540 990 $titleMid $whiteBrush
  Draw-CenteredLineSegments $g @(@{ Text = "que você importava."; Color = "white" }) 540 1060 $titleMid $whiteBrush
}

Save-Slide 2 {
  param($g)
  Draw-SlideNumber $g 2 "light"
  Draw-Logo $g "light"
  Draw-LineSegments $g @(@{ Text = "Consulta marcada"; Color = "gold" }) 76 150 $titleMid $navyBrush
  Draw-PlainLines $g @("não significa", "consulta garantida.") 76 224 $titleMid $navyBrush 4
  $g.FillRectangle($goldBrush, 76, 426, 115, 5)
  Draw-PlainLines $g @("Entre o agendamento e o horário", "da consulta, muita coisa compete", "pela atenção do paciente.") 76 492 $body $navyBrush 7
}

Save-Slide 3 {
  param($g)
  Draw-SlideNumber $g 3 "dark"
  Draw-Logo $g "dark"
  Draw-PlainLines $g @("O no-show", "começa antes", "do paciente", "faltar.") 78 158 $title $whiteBrush 0
  $g.FillRectangle($goldBrush, 78, 546, 130, 5)
  Draw-PlainLines $g @("Começa quando", "a sua clínica") 78 610 $bodyBold $whiteBrush 8
  Draw-LineSegments $g @(@{ Text = "some da cabeça"; Color = "gold" }) 78 728 $bodyBold $whiteBrush
  Draw-PlainLines $g @("dele.") 78 786 $bodyBold $whiteBrush 0
}

Save-Slide 4 {
  param($g)
  Draw-Overlay $g 0 135 1350
  Draw-SlideNumber $g 4 "dark"
  Draw-Logo $g "dark"
  Draw-PlainLines $g @("Mensagem fria", "pode até ser vista.") 76 142 $titleMid $whiteBrush 4
  $g.FillRectangle($goldBrush, 76, 320, 108, 5)
  Draw-PlainLines $g @("Mas isso não significa", "que o paciente deu", "importância.") 76 378 $body $whiteBrush 7
}

Save-Slide 5 {
  param($g)
  Draw-SlideNumber $g 5 "dark"
  Draw-Logo $g "dark"
  Draw-PlainLines $g @("Um funil de", "comparecimento", "precisa de", "três momentos:") 78 142 $titleMid $whiteBrush 0
  $g.FillRectangle($goldBrush, 78, 500, 128, 5)
  $items = @("presença,", "confirmação,", "lembrete.")
  $y = 584
  foreach ($item in $items) {
    $g.FillEllipse($goldBrush, 84, $y + 18, 14, 14)
    $g.DrawString($item, $bodyBold, $whiteBrush, 124, $y)
    $y += 76
  }
}

Save-Slide 6 {
  param($g)
  Draw-SlideNumber $g 6 "light"
  Draw-Logo $g "light"
  Draw-PlainLines $g @("A clínica precisa", "aparecer antes", "da consulta.") 76 142 $titleMid $navyBrush 2
  $g.FillRectangle($goldBrush, 76, 428, 118, 5)
  Draw-PlainLines $g @("Um dia antes.", "Algumas horas antes.", "No momento certo para", "confirmar presença.") 76 500 $body $navyBrush 9
}

Save-Slide 7 {
  param($g)
  Draw-Overlay $g 0 95 1350
  Draw-SlideNumber $g 7 "dark"
  Draw-Logo $g "dark"
  Draw-PlainLines $g @("No-show não", "se resolve só", "com agenda.") 76 140 $titleMid $whiteBrush 3
  $g.FillRectangle($goldBrush, 76, 430, 120, 5)
  Draw-LineSegments $g @(@{ Text = "Se resolve com "; Color = "white" }, @{ Text = "processo."; Color = "gold" }) 76 500 $bodyBold $whiteBrush
  Draw-PlainLines $g @("Comente NO-SHOW", "e veja como funciona", "um sistema de comparecimento", "para clínicas.") 76 610 $bodySmall $whiteBrush 9
}

$title.Dispose(); $titleBig.Dispose(); $titleMid.Dispose(); $body.Dispose(); $bodySmall.Dispose(); $bodyBold.Dispose()
$whiteBrush.Dispose(); $navyBrush.Dispose(); $goldBrush.Dispose()

# Preview grid for final slides.
$files = 1..7 | ForEach-Object { Join-Path $outDir ("slide-{0:D2}.png" -f $_) }
$thumbW = 270; $thumbH = 338; $gap = 16; $labelH = 28; $cols = 3; $rows = 3
$canvasW = ($cols * $thumbW) + (($cols + 1) * $gap)
$canvasH = ($rows * ($thumbH + $labelH)) + (($rows + 1) * $gap)
$grid = New-Object System.Drawing.Bitmap $canvasW, $canvasH
$gg = [System.Drawing.Graphics]::FromImage($grid)
$gg.Clear([System.Drawing.Color]::FromArgb(245,244,242))
$gg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$labelFont = New-Font "Candara" 18 ([System.Drawing.FontStyle]::Bold)
$labelBrush = New-Brush $navy
for ($idx=0; $idx -lt $files.Count; $idx++) {
  $img = [System.Drawing.Image]::FromFile($files[$idx])
  $col = $idx % $cols; $row = [Math]::Floor($idx / $cols)
  $x = $gap + ($col * ($thumbW + $gap))
  $y = $gap + ($row * ($thumbH + $labelH + $gap))
  $gg.DrawImage($img, $x, $y + $labelH, $thumbW, $thumbH)
  $gg.DrawString(("Slide {0:D2}" -f ($idx + 1)), $labelFont, $labelBrush, $x, $y)
  $img.Dispose()
}
$preview = Join-Path $root "preview-grid-final.jpg"
$grid.Save($preview, [System.Drawing.Imaging.ImageFormat]::Jpeg)
$labelFont.Dispose(); $labelBrush.Dispose(); $gg.Dispose(); $grid.Dispose()
Write-Output $preview
