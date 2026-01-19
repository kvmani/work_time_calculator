# Work Time Calculator (Daily)

A lightweight, air-gapped Tkinter desktop app to track daily working time from one or more intervals (e.g., T1–T2, T3–T4, …). It supports AM/PM and 24-hour inputs with seconds, allows exactly one open interval that uses the current system time, rejects cross-midnight intervals, detects overlaps, and shows worked, remaining to target (default 08:30:00, editable), overtime, and a progress bar.

Single-file. No persistence. No internet. Runs on standard Python with Tkinter.

---

## Features

- Multiple intervals per day: [Start → End] rows.
- Open interval (leave End blank) uses current system time.
- Validation: format checks, no overlaps, no cross-midnight, one open interval max, end must be after start.
- Time parsing: 9, 9:15, 9:15:30, 9 AM, 9:15 pm, 21:07, 21:07:33.
- Target time: editable (e.g., 8:30, 08:30:00, 9, 10:15:30).
- Display: Worked, Remaining (to target), Overtime, Progress %.
- Quality of life: sort by start, End = Now for selected, copy summary to clipboard.
- Help menu with visible shortcuts and rules.

---

## Requirements

- Python 3.8+
- Tkinter (bundled with most CPython installers on Windows/macOS; on some Linux distros install python3-tk).
  - Ubuntu/Debian: sudo apt-get install python3-tk

No third-party packages required.

---

## Installation & Running

1. Save the script as work_time_calculator.py.
2. Run:
   python work_time_calculator.py

The app window will open. The date uses today automatically.

---

## Quick Start

1. Enter one or more Start and End times (AM/PM or 24-hour).
2. Leave End blank for the active/ongoing interval (app will use current system time).
3. Adjust Target if needed (default 08:30:00).
4. Press Recalculate (F5).
   See Worked, Remaining, Overtime, and Progress update.

---

## Accepted Time Formats

- 12-hour: 9 AM, 9:15 pm, 12:00 AM (midnight), 12 PM (noon)
- 24-hour: 9, 09:00, 21:07, 21:07:33
- Seconds are optional in inputs; computations are accurate to seconds.

Rules:
- End must be after Start; cross-midnight intervals are rejected.
- At most one open interval (End blank).
- No overlaps; touching intervals are fine (e.g., 10:00–11:00 and 11:00–12:00).

---

## Example

Inputs
Start        End
-----------  -----------
9:00 AM      12:15 PM
1:00 PM
18:00        19:10:30

Assuming current time is 16:30:00, totals are:
- Worked = 03:15:00 + 03:30:00 + 01:10:30 = 07:55:30
- Target = 08:30:00
- Remaining = 00:34:30 (Progress ≈ 93%)

(Your values will reflect the actual system time when you recalc.)

---

## Keyboard Shortcuts (also in Help)

- F5 – Recalculate
- Ctrl+N – Add Row
- Delete – Remove Selected Rows
- Ctrl+S – Sort by Start
- Ctrl+E – End = Now for Selected Rows
- Ctrl+C – Copy Summary
- Esc – Quit

---

## GUI at a Glance (ASCII Mock)

+----------------------------------------------------------------------------+
| Work Time Calculator (Daily)                                               |
+----------------------------------------------------------------------------+
| Date: [ Today (auto) ]   Target: [ 08:30:00 ]   [Recalculate]  [Copy Sum]  |
+----------------------------------------------------------------------------+
| Intervals (Start → End)                                                    |
|  ┌────────────┬────────────┬────────────────────────────────────────────┐  |
|  |   Start    |    End     |   Validation / Notes                       |  |
|  ├────────────┼────────────┼────────────────────────────────────────────┤  |
|  |  9:00 AM   |  12:15 PM  |  OK                                        |  |
|  |  1:00 PM   |            |  Open interval → using current time 16:30  |  |
|  └────────────┴────────────┴────────────────────────────────────────────┘  |
|  [Add Row]  [Remove Selected]  [End=Now]  [Sort by Start]                 |
+----------------------------------------------------------------------------+
| Worked: 06:55:30     Remaining: 01:34:30     Overtime: 00:00:00           |
| Progress: [███████████---------]  81%                                      |
+----------------------------------------------------------------------------+
| Status: No overlaps. 1 open interval using system time 16:30:00.           |
+----------------------------------------------------------------------------+

---

## How It Works (Design Overview)

Object-Oriented Core
- TimeParser: parse times/durations; format seconds as HH:MM:SS.
- TimeInterval: single interval; supports open end; computes duration (seconds).
- DaySchedule: collection of intervals; validates constraints; sums work; computes remaining and progress.
- GuiController: Tkinter UI; manages rows, actions, validation hints, and totals.

Key Logic
- All times are anchored to today and treated as same-day only.
- Open interval uses datetime.now() (clamped to today) as its end during calculations.
- Overlap check is done on effective intervals (open interval end = now).
- Cross-midnight or end ≤ start is rejected with clear messages.

---

## Troubleshooting

- Start required / Empty row: Provide a start time or delete the row.
- Start/End time invalid: Check typos; accepted examples are listed above.
- End must be after Start (no cross-midnight): Split your work at midnight across two days.
- Only one open interval is allowed: Close or fill End for all but one open interval.
- Intervals overlap after sorting: Adjust times so intervals do not overlap.

If the Target field is invalid, the app will fall back to 08:30:00 and show a status message.

---

## Customization

- Change the default target by editing the GuiController initialization (self.var_target = ...).
- Add persistence (CSV import/export) by introducing a simple CsvIO helper (not included by default).
- To allow cross-midnight, you could auto-split into two days—but this build rejects such intervals by design.

---

## Security & Privacy

- Air-gapped: no internet calls.
- No files are written; data lives in memory only.

---

## License

Provide your preferred license (e.g., MIT) if you plan to distribute.
