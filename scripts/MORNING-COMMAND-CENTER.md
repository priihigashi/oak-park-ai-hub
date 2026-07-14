# Morning Command Center - "pop up in my face" setup

Priscila's morning launcher opens the 4 things she must see first thing, then reminds her to run `/focus`.
It opens: her **Daily Journal folder**, the **Focus Partner sheet**, the **money dashboard**, and her **Boletim Diario** daily briefing.

Portable launchers in this repo: `scripts/focus-morning.bat` (Windows) and `scripts/focus-morning.command` (Mac).

## The 4 links it opens
- Journal folder: https://drive.google.com/drive/folders/1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB
- Focus Partner sheet: https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c
- Money dashboard (Finance Dashboard - PRI 2026): https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64
- Boletim Diario (daily briefing): https://priihigashi.github.io/ClaudeGallery/boletim-diario.html

## Windows (Claude PC) - DONE
- Script: `C:\Users\Admin\FocusMorning\focus-morning.bat` (copy of `scripts/focus-morning.bat`).
- Desktop shortcut: **"Start Focus"** - double-click anytime.
- Auto: Task Scheduler task **"Focus Morning"** runs it daily at 10:00.
- Stop the auto-open:  `schtasks /delete /tn "Focus Morning" /f`  |  Change time:  `schtasks /change /tn "Focus Morning" /st HH:MM`

## Mac - READY (one-time hookup)
1. Download `scripts/focus-morning.command` to your Mac (e.g. into your home folder).
2. In Terminal: `chmod +x ~/focus-morning.command` (makes it runnable). Double-click to test - it should open the 4 tabs.
3. Pick ONE auto-trigger:
   - **Login Item** (opens when the Mac starts): System Settings > General > Login Items > "+" > choose `focus-morning.command`.
   - **Shortcuts @10:00** (opens every day at 10): Shortcuts app > new Shortcut > add 4 "Open URLs" actions (the 4 links) > then Automation tab > "+" > Time of Day > 10:00 Daily > run the shortcut (turn OFF "Ask Before Running").

## iPhone - READY (Shortcuts)
1. Shortcuts app > Shortcuts tab > "+" to create one named "Start Focus".
2. Add 4 **Open URLs** actions, one per link above (or one Open URLs action with all 4).
3. Automation tab > "+" > Time of Day > 10:00 > Daily > Next > pick the "Start Focus" shortcut > turn OFF "Ask Before Running".
4. (Optional) also add the Boletim as an "Add to Home Screen" web app for one-tap.

## Rule
This is a nudge layer, not the source of truth. The board of record is `.claude/focus-partner-state.md`. Opening the links is NOT doing the work - the point is to make Priscila SEE it so she starts. After it opens, she runs `/focus` (manifestation first, then Today's 3).
