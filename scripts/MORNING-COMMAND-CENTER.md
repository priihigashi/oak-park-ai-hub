# Morning Command Center - "pop up in my face" setup

Priscila's morning launcher opens the 3 things she must see first thing, then reminds her to run `/focus`.
It opens: her **Daily Journal folder**, the **Focus Partner sheet**, and the **money dashboard**.

The portable launcher is `scripts/focus-morning.bat` (Windows). Per-device setup is below.

## The 3 links it opens
- Journal folder: https://drive.google.com/drive/folders/1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB
- Focus Partner sheet: https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c
- Money dashboard (Finance Dashboard - PRI 2026): https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64

## Windows (Claude PC) - DONE 2026-07-14
- Script: `C:\Users\Admin\FocusMorning\focus-morning.bat` (copy of `scripts/focus-morning.bat`).
- Desktop shortcut: **"Start Focus"** - double-click anytime.
- Auto: Task Scheduler task **"Focus Morning"** runs it daily at 10:00.
- To STOP the auto-open:  `schtasks /delete /tn "Focus Morning" /f`
- To change the time:     `schtasks /change /tn "Focus Morning" /st HH:MM`

## Mac - TODO
- Option A (Login Item): System Settings > General > Login Items > add a small `.command` file that runs: `open "URL1" "URL2" "URL3"`
- Option B (Shortcuts app): new Shortcut with 3 "Open URLs" actions, then Automations > Time of Day > 10:00 > run it.

## iPhone - TODO
- Shortcuts app > new Shortcut "Start Focus" with 3 "Open URLs" actions > Automations > Time of Day 10:00 (or "When I open Notability") > run.

## Rule
This is a nudge layer, not the source of truth. The board of record is `.claude/focus-partner-state.md`. Opening the links is NOT doing the work - the point is to make Priscila SEE it so she starts. After it opens, she runs `/focus` (manifestation first, then Today's 3).
