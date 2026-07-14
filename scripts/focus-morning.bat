@echo off
title Focus Partner - Morning Command Center
rem === Priscila's "pop up in my face" morning launcher ===
rem Opens the 4 things she should see first thing, then tells her to run /focus.
rem Managed by Focus Partner. To STOP the daily auto-open:  schtasks /delete /tn "Focus Morning" /f

start "" "https://drive.google.com/drive/folders/1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB"
start "" "https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c"
start "" "https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64"
start "" "https://priihigashi.github.io/ClaudeGallery/boletim-diario.html"

echo.
echo   ==================================================
echo      GOOD MORNING, PRISCILA  --  START FOCUS
echo   ==================================================
echo      [1] Journal folder ........ opened
echo      [2] Focus Partner sheet ... opened
echo      [3] Money dashboard ....... opened
echo      [4] Boletim (daily brief) . opened
echo.
echo      NOW: open Claude Code and type   /focus
echo      -> manifestation first, then today's 3.
echo   ==================================================
echo.
timeout /t 25
