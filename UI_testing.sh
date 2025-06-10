# set your waits once up front
$packageDir      = ""
$dumpXmlDir      = ""
$screenshotDir   = ""
$postLaunchWait  = 1   # 1 at least
$downloadWait    = 15  # 15 at least
$screenshotWait  = 8  # 8 at least

function Stop-HealthConnect {
    .\adb shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS `
        -d "package:com.google.android.apps.healthdata"
    Start-Sleep -Seconds $postLaunchWait
    .\adb shell am force-stop com.google.android.healthconnect.controller
    Start-Sleep -Seconds 3
}

function Uninstall-App {
    param($pkg)
    .\adb shell am start -a android.intent.action.VIEW -d "market://details?id=$pkg"
    Start-Sleep -Seconds $postLaunchWait
    .\adb shell uiautomator dump /sdcard/uninstall_dump.xml
    .\adb pull /sdcard/uninstall_dump.xml "$dumpXmlDir\uninstall_dump.xml"
    [xml]$uDoc = Get-Content "$dumpXmlDir\uninstall_dump.xml" -Raw
    $uNode = $uDoc.SelectSingleNode("//node[contains(@text,'Uninstall')]")
    if ($uNode -and $uNode.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        $ux = ([int]$matches[1] + [int]$matches[3]) / 2
        $uy = ([int]$matches[2] + [int]$matches[4]) / 2
        .\adb shell input tap $ux $uy
        # confirm uninstall dialog
        .\adb shell input tap 840 1350
    }
}

$apkFiles = Get-ChildItem -Path $packageDir -Filter *.apk

foreach ($apk in $apkFiles) {
    $package = [IO.Path]::GetFileNameWithoutExtension($apk.Name)

    # ←––––– NEW: skip if screenshot already exists
    $already = Join-Path $screenshotDir "screen_$package.png"
    if (Test-Path $already) {
        Write-Host "=== Skipping $package (screenshot exists) ==="
        continue
    }

    Write-Host "=== Processing package: $package ==="

    # --- Step 1: Install or skip+ss ---
    .\adb shell am start -a android.intent.action.VIEW -d "market://details?id=$package"
    Start-Sleep -Seconds $postLaunchWait

    .\adb shell uiautomator dump /sdcard/install_dump.xml
    .\adb pull /sdcard/install_dump.xml "$dumpXmlDir\install_dump.xml"
    [xml]$doc = Get-Content "$dumpXmlDir\install_dump.xml" -Raw

    $node = $doc.SelectSingleNode("//node[contains(@text,'Install')]")
    if ($node -and $node.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        $x = ([int]$matches[1] + [int]$matches[3]) / 2
        $y = ([int]$matches[2] + [int]$matches[4]) / 2
        .\adb shell input tap $x $y
    }
    else {
        Write-Host "No Install → screenshot & skip"
        Start-Sleep -Seconds $screenshotWait
        .\adb shell screencap -p "/sdcard/screen_$package.png"
        .\adb pull "/sdcard/screen_$package.png" "$screenshotDir\screen_$package.png"
        Stop-HealthConnect
        Uninstall-App $package
        continue
    }
    Start-Sleep -Seconds $downloadWait

    # --- Step 2: Open HC & tap “Open” ---
    .\adb shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS `
        -d "package:com.google.android.apps.healthdata"
    Start-Sleep -Seconds $postLaunchWait
    .\adb shell input tap 950 180
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 3: dump App Permissions ---
    .\adb shell uiautomator dump /sdcard/ap_dump.xml
    .\adb pull /sdcard/ap_dump.xml "$dumpXmlDir\ap_dump.xml"
    [xml]$doc = Get-Content "$dumpXmlDir\ap_dump.xml" -Raw
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 4: tap “App permissions” ---
    $node = $doc.SelectSingleNode("//node[contains(@text,'App permissions')]")
    if ($node -and $node.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        $x = ([int]$matches[1] + [int]$matches[3]) / 2
        $y = ([int]$matches[2] + [int]$matches[4]) / 2
        .\adb shell input tap $x $y
    }
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 5: “Not allowed access” OR both present → skip+ss ---
    .\adb shell uiautomator dump /sdcard/ca_dump.xml
    .\adb pull /sdcard/ca_dump.xml "$dumpXmlDir\ca_dump.xml"
    [xml]$doc = Get-Content "$dumpXmlDir\ca_dump.xml" -Raw

    $na        = $doc.SelectSingleNode("//node[contains(@text,'Not allowed access')]")
    $noDenied  = $doc.SelectSingleNode("//node[contains(@text,'No apps denied')]")
    if ($na -and $noDenied) {
        Write-Host "Both 'Not allowed access' and 'No apps denied' → screenshot & skip"
        Start-Sleep -Seconds $screenshotWait
        .\adb shell screencap -p "/sdcard/screen_$package.png"
        .\adb pull "/sdcard/screen_$package.png" "$screenshotDir\screen_$package.png"
        Stop-HealthConnect
        Uninstall-App $package
        continue
    }
    elseif ($na -and $na.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        $x = ([int]$matches[1] + [int]$matches[3]) / 2
        $y = ([int]$matches[2] + [int]$matches[4]) / 2 + 100
        .\adb shell input tap $x $y
    }
    else {
        Write-Host "No Not allowed access → screenshot & skip"
        Start-Sleep -Seconds $screenshotWait
        .\adb shell screencap -p "/sdcard/screen_$package.png"
        .\adb pull "/sdcard/screen_$package.png" "$screenshotDir\screen_$package.png"
        Stop-HealthConnect
        Uninstall-App $package
        continue
    }
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 6: scroll down ---  3 at least
    1..3 | ForEach-Object {
        .\adb shell input swipe 500 1800 500 600 500
        Start-Sleep -Seconds 1
    }
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 7: tap “Read privacy policy” or skip+ss ---
    .\adb shell uiautomator dump /sdcard/rpp_dump.xml
    .\adb pull /sdcard/rpp_dump.xml "$dumpXmlDir\rpp_dump.xml"
    [xml]$doc = Get-Content "$dumpXmlDir\rpp_dump.xml" -Raw

    $pp = $doc.SelectSingleNode("//node[contains(@text,'Read privacy policy')]")
    if ($pp -and $pp.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        $x = ([int]$matches[1] + [int]$matches[3]) / 2
        $y = ([int]$matches[2] + [int]$matches[4]) / 2
        .\adb shell input tap $x $y
    }
    else {
        Write-Host "No Read privacy policy → screenshot & skip"
        Start-Sleep -Seconds $screenshotWait
        .\adb shell screencap -p "/sdcard/screen_$package.png"
        .\adb pull "/sdcard/screen_$package.png" "$screenshotDir\screen_$package.png"
        Stop-HealthConnect
        Uninstall-App $package
        continue
    }
    Start-Sleep -Seconds $postLaunchWait

    # --- Step 8: screenshot the policy page ---
    Start-Sleep -Seconds $screenshotWait
    .\adb shell screencap -p "/sdcard/screen_$package.png"
    .\adb pull "/sdcard/screen_$package.png" "$screenshotDir\screen_$package.png"

    # go back three times to return up in the UI
    1..3 | ForEach-Object {
        .\adb shell input keyevent 4
        Start-Sleep -Seconds 1
    }

    # now dump UI to see if a "Close app" button appeared (crash dialog)
    .\adb shell uiautomator dump /sdcard/crash_dump.xml
    .\adb pull /sdcard/crash_dump.xml "$dumpXmlDir\crash_dump.xml"
    [xml]$cDoc = Get-Content "$dumpXmlDir\crash_dump.xml" -Raw

    $closeNode = $cDoc.SelectSingleNode("//node[contains(@text,'Close app')]")
    if ($closeNode -and $closeNode.GetAttribute("bounds") -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
        # tap the "Close app" button
        $cx = ([int]$matches[1] + [int]$matches[3]) / 2
        $cy = ([int]$matches[2] + [int]$matches[4]) / 2
        .\adb shell input tap $cx $cy

        # then cleanup & uninstall before moving on
        Stop-HealthConnect
        Uninstall-App $package
        continue
    }

    # --- Step 9: force‑stop HC before uninstall ---
    Stop-HealthConnect

    # --- Step 10: Uninstall from Play Store (normal flow) ---
    Uninstall-App $package

    Write-Host "=== Done with $package ===`n"
}
