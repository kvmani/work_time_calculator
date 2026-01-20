#!/usr/bin/env python3
"""
Work Time Calculator (Daily) - Tkinter GUI
- Air-gapped, no persistence.
- Multiple intervals (start/end) with optional single open interval (end blank -> uses now).
- Rejects cross-midnight; detects overlaps; end must be after start.
- Target duration editable (default 08:30:00).
- Shows CURRENT TIME prominently (bold), totals, and a bold milestone message:
   - If below target: time left to reach target and the absolute clock time when you’ll hit it.
   - If at/above target: overtime, time left to next whole overtime hour, and the absolute clock time when you’ll hit it.
- Important policy: If you are checking the app, you are assumed to be working now for milestone projections,
  even if there is no open interval row. (Totals still depend on entered intervals.)

Run:
  python work_time_calculator.py
"""

from __future__ import annotations

import os
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, date, time


def _is_wsl() -> bool:
    rel = platform.release().lower()
    return (
        "microsoft" in rel
        or "wsl" in rel
        or "WSL_INTEROP" in os.environ
        or "WSL_DISTRO_NAME" in os.environ
    )


def _print_tkinter_import_help(err: Exception) -> None:
    lines = [
        "ERROR: Tkinter is not available. This app requires Tk.",
        f"Import error: {err}",
    ]
    if sys.platform.startswith("linux"):
        lines.extend(
            [
                "Install Tk using your OS package manager (not pip).",
                "Ubuntu/Debian: sudo apt-get install -y python3-tk",
                "Fedora: sudo dnf install python3-tkinter",
                "Arch: sudo pacman -S tk",
                "Then verify with: python3 -m tkinter",
            ]
        )
    elif sys.platform == "win32":
        lines.extend(
            [
                "On Windows, install Python from python.org and ensure Tcl/Tk is selected.",
                "Then verify with: py -m tkinter",
            ]
        )
    else:
        lines.append("Install a Python build that includes Tk, then retry.")
    sys.stderr.write("\n".join(lines) + "\n")


def _print_tkinter_display_help(err: Exception) -> None:
    lines = [
        "ERROR: Tkinter could not open a GUI window.",
        f"GUI error: {err}",
    ]
    if sys.platform.startswith("linux"):
        if _is_wsl():
            lines.extend(
                [
                    "If you are in WSL, enable WSLg (Windows 11) or use an X server.",
                    "Ensure DISPLAY/WAYLAND_DISPLAY is set for your session.",
                ]
            )
        else:
            lines.append("Ensure a desktop session is available and DISPLAY is set.")
    sys.stderr.write("\n".join(lines) + "\n")


try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import tkinter.font as tkfont
except Exception as exc:
    _print_tkinter_import_help(exc)
    raise SystemExit(1)


# ----------------------------- Utilities & Parsing -----------------------------

class TimeParser:
    """
    Parses times and durations:
      - Times: '9', '9 am', '9:15', '9:15 pm', '09:15:20', '21:07', '12 pm', '12:00 am'
      - Duration: '8:30', '08:30:00', '9', '10:15:30'
    Formats seconds as 'HH:MM:SS'.
    """

    _am_pm_re = re.compile(r"\s*(am|pm)\s*$", re.IGNORECASE)

    @staticmethod
    def parse_time(text: str) -> time:
        """
        Parse a clock time (same day).
        Accepts 12h/24h with optional seconds and AM/PM.
        Raises ValueError on failure.
        """
        s = (text or "").strip()
        if not s:
            raise ValueError("Empty time")

        # Detect AM/PM
        ampm = None
        m = TimeParser._am_pm_re.search(s)
        if m:
            ampm = m.group(1).lower()
            s = TimeParser._am_pm_re.sub("", s).strip()

        parts = s.split(":")
        if len(parts) > 3:
            raise ValueError("Too many ':' in time")

        try:
            hh = int(parts[0])
            mm = int(parts[1]) if len(parts) >= 2 and parts[1] != "" else 0
            ss = int(parts[2]) if len(parts) == 3 and parts[2] != "" else 0
        except ValueError:
            raise ValueError("Non-numeric time component")

        if mm not in range(0, 60) or ss not in range(0, 60):
            raise ValueError("Minutes/seconds out of range")

        if ampm:
            if hh not in range(1, 13):
                raise ValueError("Hour out of range for 12-hour time")
            if ampm == "am":
                hh = 0 if hh == 12 else hh
            else:
                hh = 12 if hh == 12 else hh + 12
        else:
            if hh not in range(0, 24):
                raise ValueError("Hour out of range for 24-hour time")

        return time(hour=hh, minute=mm, second=ss)

    @staticmethod
    def parse_duration(text: str) -> int:
        """
        Parse duration 'H', 'H:MM', 'H:MM:SS' into seconds.
        Raises ValueError on failure.
        """
        s = (text or "").strip()
        if not s:
            raise ValueError("Empty duration")

        parts = s.split(":")
        if len(parts) > 3:
            raise ValueError("Too many ':' in duration")

        try:
            if len(parts) == 1:
                h = int(parts[0]); m = 0; sec = 0
            elif len(parts) == 2:
                h = int(parts[0]); m = int(parts[1]); sec = 0
            else:
                h = int(parts[0]); m = int(parts[1]); sec = int(parts[2])
        except ValueError:
            raise ValueError("Non-numeric duration component")

        if h < 0 or m not in range(0, 60) or sec not in range(0, 60):
            raise ValueError("Invalid duration values")

        return h * 3600 + m * 60 + sec

    @staticmethod
    def format_hms(seconds: int) -> str:
        sign = "-" if seconds < 0 else ""
        s = abs(int(seconds))
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{sign}{h:02d}:{m:02d}:{sec:02d}"


# ----------------------------- Domain Model -----------------------------------

@dataclass
class TimeInterval:
    start: time
    end: time | None  # None means open interval

    def is_open(self) -> bool:
        return self.end is None

    def duration_seconds(self, on_date: date, now_dt: datetime) -> int:
        """
        Duration in seconds. Open interval uses now_dt.
        Rejects cross-midnight/end-before-start.
        """
        start_dt = datetime.combine(on_date, self.start)
        end_dt = now_dt if self.is_open() else datetime.combine(on_date, self.end)

        if end_dt <= start_dt:
            # end == start => 0 duration not allowed as an interval; treat as invalid
            raise ValueError("End must be after Start within the same day (no cross-midnight).")

        return int((end_dt - start_dt).total_seconds())


class DaySchedule:
    def __init__(self, on_date: date, target_seconds: int = 8 * 3600 + 30 * 60):
        self.on_date = on_date
        self.intervals: list[TimeInterval] = []
        self.target_seconds = target_seconds

    def set_intervals(self, intervals: list[TimeInterval]) -> None:
        self.intervals = list(intervals)

    def sorted_intervals(self) -> list[TimeInterval]:
        return sorted(self.intervals, key=lambda it: it.start)

    def validate(self, now_dt: datetime) -> list[str]:
        msgs: list[str] = []

        open_count = sum(1 for it in self.intervals if it.is_open())
        if open_count > 1:
            msgs.append("Only one open interval is allowed.")

        # Build effective start/end datetimes
        effective = []
        for it in self.sorted_intervals():
            start_dt = datetime.combine(self.on_date, it.start)
            end_dt = now_dt if it.is_open() else datetime.combine(self.on_date, it.end)
            if end_dt <= start_dt:
                msgs.append("End must be after Start within the same day (no cross-midnight).")
            effective.append((start_dt, end_dt))

        # Overlap check (touching is fine)
        effective.sort(key=lambda t: t[0])
        for i in range(1, len(effective)):
            prev_end = effective[i - 1][1]
            this_start = effective[i][0]
            if this_start < prev_end:
                msgs.append("Intervals overlap after sorting.")
                break

        return msgs

    def total_worked_seconds(self, now_dt: datetime) -> int:
        total = 0
        for it in self.intervals:
            total += it.duration_seconds(self.on_date, now_dt)
        return total

    def remaining_seconds(self, now_dt: datetime) -> int:
        return self.target_seconds - self.total_worked_seconds(now_dt)


# ----------------------------- GUI --------------------------------------------

class IntervalRow:
    """
    One editable row: Start Entry, End Entry, Select checkbox, Notes Label.
    """
    def __init__(self, master: tk.Frame, on_change_cb):
        self.master = master
        self.on_change_cb = on_change_cb

        self.var_start = tk.StringVar()
        self.var_end = tk.StringVar()
        self.var_select = tk.BooleanVar(value=False)

        self.ent_start = ttk.Entry(master, textvariable=self.var_start, width=14)
        self.ent_end = ttk.Entry(master, textvariable=self.var_end, width=14)
        self.chk_sel = ttk.Checkbutton(master, variable=self.var_select)
        self.lbl_note = ttk.Label(master, text="", anchor="w")

        for w in (self.ent_start, self.ent_end):
            w.bind("<KeyRelease>", self._on_change)

    def _on_change(self, event=None):
        if callable(self.on_change_cb):
            self.on_change_cb()

    def grid(self, r: int):
        self.ent_start.grid(row=r, column=0, padx=4, pady=2, sticky="ew")
        self.ent_end.grid(row=r, column=1, padx=4, pady=2, sticky="ew")
        self.chk_sel.grid(row=r, column=2, padx=4, pady=2)
        self.lbl_note.grid(row=r, column=3, padx=4, pady=2, sticky="ew")

    def destroy(self):
        self.ent_start.destroy()
        self.ent_end.destroy()
        self.chk_sel.destroy()
        self.lbl_note.destroy()

    def is_selected(self) -> bool:
        return bool(self.var_select.get())

    def set_note(self, text: str):
        self.lbl_note.config(text=text)

    def get_interval_or_error(self) -> tuple[TimeInterval | None, str | None]:
        start_txt = self.var_start.get().strip()
        end_txt = self.var_end.get().strip()

        if not start_txt and not end_txt:
            return None, None  # empty row is fine
        if not start_txt:
            return None, "Start required"

        try:
            start_t = TimeParser.parse_time(start_txt)
        except ValueError as e:
            return None, f"Start invalid: {e}"

        if end_txt == "":
            return TimeInterval(start=start_t, end=None), None

        try:
            end_t = TimeParser.parse_time(end_txt)
        except ValueError as e:
            return None, f"End invalid: {e}"

        # quick semantic check (cross-midnight / end<=start)
        if datetime.combine(date.today(), end_t) <= datetime.combine(date.today(), start_t):
            return None, "End must be after Start (no cross-midnight)"

        return TimeInterval(start=start_t, end=end_t), None


class GuiController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Work Time Calculator (Daily)")
        self.root.minsize(900, 520)

        self._recalc_after_id = None

        # Fonts for bold prominent labels
        default_font = tkfont.nametofont("TkDefaultFont")
        self.font_big_bold = default_font.copy()
        self.font_big_bold.configure(size=max(default_font.cget("size") + 6, 14), weight="bold")

        self.font_bold = default_font.copy()
        self.font_bold.configure(weight="bold")

        # Containers
        self.frm_top = ttk.Frame(root, padding=8)
        self.frm_top.pack(fill="x")

        self.frm_time = ttk.Frame(root, padding=(8, 0, 8, 0))
        self.frm_time.pack(fill="x")

        self.frm_table_hdr = ttk.Frame(root, padding=(8, 0, 8, 0))
        self.frm_table_hdr.pack(fill="x")

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.frm_table = ttk.Frame(self.canvas)
        self.scroll_y = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 0))
        self.scroll_y.pack(side="right", fill="y", padx=(0, 8))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frm_table, anchor="nw")
        self.frm_table.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.frm_buttons = ttk.Frame(root, padding=8)
        self.frm_buttons.pack(fill="x")

        self.frm_totals = ttk.Frame(root, padding=(8, 6, 8, 6))
        self.frm_totals.pack(fill="x")

        self.frm_milestone = ttk.LabelFrame(root, text="Milestone", padding=10)
        self.frm_milestone.pack(fill="x", padx=8, pady=(0, 8))

        self.frm_status = ttk.Frame(root, padding=(8, 0, 8, 8))
        self.frm_status.pack(fill="x")

        # Top controls
        today_str = date.today().strftime("%Y-%m-%d")
        ttk.Label(self.frm_top, text=f"Date: {today_str}").pack(side="left")
        ttk.Label(self.frm_top, text="   Target:").pack(side="left")

        self.var_target = tk.StringVar(value="08:30:00")
        self.ent_target = ttk.Entry(self.frm_top, textvariable=self.var_target, width=10)
        self.ent_target.pack(side="left", padx=(4, 8))

        self.btn_recalc = ttk.Button(self.frm_top, text="Recalculate (F5)", command=self.recalculate)
        self.btn_recalc.pack(side="left", padx=4)

        self.btn_copy = ttk.Button(self.frm_top, text="Copy Summary (Ctrl+C)", command=self.copy_summary)
        self.btn_copy.pack(side="left", padx=4)

        # Current time prominently
        self.var_now = tk.StringVar(value="--:--:--")
        ttk.Label(self.frm_time, text="CURRENT TIME:", font=self.font_big_bold).pack(side="left", padx=(0, 10))
        self.lbl_now = ttk.Label(self.frm_time, textvariable=self.var_now, font=self.font_big_bold)
        self.lbl_now.pack(side="left")

        # Table header
        ttk.Label(self.frm_table_hdr, text="Start (e.g., 9:00 AM or 09:00:00)", width=32).grid(row=0, column=0, padx=4, pady=(6, 2), sticky="w")
        ttk.Label(self.frm_table_hdr, text="End (blank = open interval)", width=28).grid(row=0, column=1, padx=4, pady=(6, 2), sticky="w")
        ttk.Label(self.frm_table_hdr, text="Select", width=8).grid(row=0, column=2, padx=4, pady=(6, 2), sticky="w")
        ttk.Label(self.frm_table_hdr, text="Validation / Notes").grid(row=0, column=3, padx=4, pady=(6, 2), sticky="w")

        # Rows
        self.rows: list[IntervalRow] = []
        for _ in range(3):
            self.add_row()

        # Buttons
        ttk.Button(self.frm_buttons, text="Add Row (Ctrl+N)", command=self.add_row).pack(side="left", padx=4)
        ttk.Button(self.frm_buttons, text="Remove Selected (Del)", command=self.remove_selected).pack(side="left", padx=4)
        ttk.Button(self.frm_buttons, text="End = Now for Selected (Ctrl+E)", command=self.end_now_for_selected).pack(side="left", padx=4)
        ttk.Button(self.frm_buttons, text="Sort by Start (Ctrl+S)", command=self.sort_by_start).pack(side="left", padx=4)
        ttk.Button(self.frm_buttons, text="Quit (Esc)", command=self.root.destroy).pack(side="right", padx=4)

        # Totals
        self.var_worked = tk.StringVar(value="00:00:00")
        self.var_remaining = tk.StringVar(value="08:30:00")
        self.var_overtime = tk.StringVar(value="00:00:00")

        self.lbl_totals = ttk.Label(
            self.frm_totals,
            text="Worked: 00:00:00    Remaining: 08:30:00    Overtime: 00:00:00",
            font=self.font_bold
        )
        self.lbl_totals.pack(side="top", anchor="w")

        self.progress = ttk.Progressbar(self.frm_totals, orient="horizontal", mode="determinate", length=360)
        self.progress.pack(side="left", padx=(0, 10), pady=(6, 0))
        self.var_progress = tk.StringVar(value="0%")
        ttk.Label(self.frm_totals, textvariable=self.var_progress).pack(side="left", pady=(6, 0))

        # Milestone text (bold)
        self.var_milestone_1 = tk.StringVar(value="")
        self.var_milestone_2 = tk.StringVar(value="")
        self.lbl_m1 = ttk.Label(self.frm_milestone, textvariable=self.var_milestone_1, font=self.font_bold)
        self.lbl_m2 = ttk.Label(self.frm_milestone, textvariable=self.var_milestone_2, font=self.font_bold)
        self.lbl_m1.pack(anchor="w")
        self.lbl_m2.pack(anchor="w", pady=(6, 0))

        # Status line
        self.var_status = tk.StringVar(value="Ready.")
        ttk.Label(self.frm_status, textvariable=self.var_status).pack(side="left", anchor="w")

        # Help menu
        self._build_menu()

        # Key bindings
        root.bind("<F5>", lambda e: self.recalculate())
        root.bind("<Control-n>", lambda e: self.add_row())
        root.bind("<Control-N>", lambda e: self.add_row())
        root.bind("<Delete>", lambda e: self.remove_selected())
        root.bind("<Control-s>", lambda e: self.sort_by_start())
        root.bind("<Control-S>", lambda e: self.sort_by_start())
        root.bind("<Escape>", lambda e: self.root.destroy())
        root.bind("<Control-e>", lambda e: self.end_now_for_selected())
        root.bind("<Control-E>", lambda e: self.end_now_for_selected())
        root.bind("<Control-c>", lambda e: self.copy_summary())
        root.bind("<Control-C>", lambda e: self.copy_summary())

        # Start live clock
        self._tick_clock()

        # Initial calculation
        self.recalculate()

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        helpmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=helpmenu)

        help_text = (
            "Shortcuts:\n"
            "  F5            – Recalculate\n"
            "  Ctrl+N        – Add Row\n"
            "  Delete        – Remove Selected Rows\n"
            "  Ctrl+S        – Sort by Start\n"
            "  Ctrl+E        – End = Now for Selected Rows\n"
            "  Ctrl+C        – Copy Summary\n"
            "  Esc           – Quit\n\n"
            "Time formats accepted:\n"
            "  9, 9:15, 9:15:30, 9 AM, 9:15 pm, 21:07, 21:07:33\n\n"
            "Rules:\n"
            "  • Only one open interval (End blank) is allowed.\n"
            "  • End must be after Start; cross-midnight intervals are rejected.\n"
            "  • Intervals must not overlap; touching is fine.\n\n"
            "Milestones:\n"
            "  The app assumes you are working if you are checking it.\n"
            "  Milestone clock times are computed as NOW + remaining time."
        )
        helpmenu.add_command(label="Usage & Shortcuts", command=lambda: messagebox.showinfo("Help", help_text))

    def _tick_clock(self):
        now_dt = datetime.now().replace(microsecond=0)
        self.var_now.set(now_dt.strftime("%H:%M:%S"))
        # Optional: keep milestones current without manual recalc
        self._schedule_recalc()
        self.root.after(1000, self._tick_clock)

    def _schedule_recalc(self):
        # Debounce recalculation during typing/clock ticks
        if self._recalc_after_id is not None:
            try:
                self.root.after_cancel(self._recalc_after_id)
            except Exception:
                pass
        self._recalc_after_id = self.root.after(200, self.recalculate)

    def add_row(self):
        row = IntervalRow(self.frm_table, on_change_cb=self._schedule_recalc)
        self.rows.append(row)
        self._regrid_rows()
        return row

    def _regrid_rows(self):
        for i, row in enumerate(self.rows, start=1):
            row.grid(i)

    def remove_selected(self):
        removed = 0
        for row in list(self.rows)[::-1]:
            if row.is_selected():
                row.destroy()
                self.rows.remove(row)
                removed += 1
        if removed == 0:
            messagebox.showinfo("Remove Selected", "No rows are selected.")
        self._regrid_rows()
        self.recalculate()

    def end_now_for_selected(self):
        now = datetime.now().time().replace(microsecond=0)
        now_str = now.strftime("%H:%M:%S")
        for row in self.rows:
            if row.is_selected():
                if row.var_start.get().strip() and not row.var_end.get().strip():
                    row.var_end.set(now_str)
        self.recalculate()

    def sort_by_start(self):
        def keyf(r: IntervalRow):
            txt = r.var_start.get().strip()
            if not txt:
                return time(23, 59, 59)
            try:
                return TimeParser.parse_time(txt)
            except Exception:
                return time(23, 59, 59)

        # Capture values
        snapshot = [(r.var_start.get(), r.var_end.get(), r.var_select.get()) for r in self.rows]
        snapshot.sort(key=lambda t: keyf(self._fake_row_for_sort(t[0])))
        # Rebuild rows cleanly (simpler than moving widgets)
        for r in self.rows:
            r.destroy()
        self.rows = []
        for s, e, sel in snapshot:
            r = self.add_row()
            r.var_start.set(s)
            r.var_end.set(e)
            r.var_select.set(sel)
        self.recalculate()

    def _fake_row_for_sort(self, start_text: str) -> IntervalRow:
        # Lightweight helper to reuse keyf; not attached to UI
        class _Fake:
            def __init__(self, t): self.var_start = type("V", (), {"get": lambda self2: t})()
        return _Fake(start_text)  # type: ignore

    def _collect_schedule(self) -> tuple[DaySchedule, list[str]]:
        now_dt = datetime.now().replace(microsecond=0)
        schedule = DaySchedule(on_date=date.today())

        intervals: list[TimeInterval] = []
        any_errors = False

        for row in self.rows:
            it, err = row.get_interval_or_error()
            if err:
                row.set_note(err)
                any_errors = True
                continue
            if it is None:
                row.set_note("")
                continue

            # Row-level note
            if it.is_open():
                row.set_note(f"Open interval → using current time {now_dt.strftime('%H:%M:%S')}")
            else:
                row.set_note("OK")

            intervals.append(it)

        schedule.set_intervals(intervals)
        val_msgs = schedule.validate(now_dt)

        # If row-level errors exist, prefer those in status too
        if any_errors and not val_msgs:
            val_msgs = ["Fix invalid rows."]

        return schedule, val_msgs

    @staticmethod
    def _ceil_to_next_hour(seconds: int) -> int:
        """
        For a positive number of seconds (overtime), returns the overtime seconds needed
        to reach the next whole hour of overtime. If already at whole hour, returns 0.
        """
        if seconds <= 0:
            return 0
        rem = seconds % 3600
        return 0 if rem == 0 else (3600 - rem)

    def _set_milestone_message(self, worked: int, target: int, now_dt: datetime):
        """
        Sets the bold milestone message.
        Policy: If you are checking the app, you are working now, so absolute times are NOW + delta.
        """
        if target <= 0:
            self.var_milestone_1.set("Target is 00:00:00 (or invalid).")
            self.var_milestone_2.set("")
            return

        if worked < target:
            remaining = target - worked
            hit_time = (now_dt + (now_dt - now_dt) + (now_dt - now_dt))  # placeholder removed below

            hit_time = now_dt + _seconds_to_timedelta(remaining)
            self.var_milestone_1.set(
                f"{TimeParser.format_hms(remaining)} left to reach target {TimeParser.format_hms(target)}."
            )
            self.var_milestone_2.set(
                f"If you keep working, you’ll reach the target at: {hit_time.strftime('%H:%M:%S')}"
            )
            return

        # worked >= target
        overtime = worked - target
        to_next = self._ceil_to_next_hour(overtime)
        overtime_hms = TimeParser.format_hms(overtime)

        if to_next == 0:
            self.var_milestone_1.set(
                f"Overtime: {overtime_hms}. You are already at a whole extra hour."
            )
            # Next whole hour after current whole hour is +1h (optional but useful)
            next_time = now_dt + _seconds_to_timedelta(3600)
            self.var_milestone_2.set(
                f"Next overtime whole-hour milestone (+01:00:00) at: {next_time.strftime('%H:%M:%S')}"
            )
        else:
            next_whole_overtime = overtime + to_next
            when = now_dt + _seconds_to_timedelta(to_next)
            self.var_milestone_1.set(
                f"Overtime: {overtime_hms}. {TimeParser.format_hms(to_next)} more to reach extra {TimeParser.format_hms(next_whole_overtime)}."
            )
            self.var_milestone_2.set(
                f"If you keep working, you’ll reach that at: {when.strftime('%H:%M:%S')}"
            )

    def recalculate(self):
        now_dt = datetime.now().replace(microsecond=0)
        schedule, val_msgs = self._collect_schedule()

        # Parse target
        try:
            schedule.target_seconds = TimeParser.parse_duration(self.var_target.get())
        except ValueError as e:
            self.var_status.set(f"Target invalid: {e} (using 08:30:00)")
            schedule.target_seconds = 8 * 3600 + 30 * 60

        if val_msgs:
            self.var_status.set(" ; ".join(dict.fromkeys(val_msgs)))
        else:
            self.var_status.set("OK.")

        # Compute totals safely
        worked = 0
        if not val_msgs:
            try:
                worked = schedule.total_worked_seconds(now_dt)
            except Exception as e:
                self.var_status.set(f"Error computing totals: {e}")
                worked = 0

        target = schedule.target_seconds
        remaining = max(0, target - worked)
        overtime = max(0, worked - target)

        self.var_worked.set(TimeParser.format_hms(worked))
        self.var_remaining.set(TimeParser.format_hms(remaining))
        self.var_overtime.set(TimeParser.format_hms(overtime))

        self.lbl_totals.config(
            text=f"Worked: {self.var_worked.get()}    "
                 f"Remaining: {self.var_remaining.get()}    "
                 f"Overtime: {self.var_overtime.get()}"
        )

        # Progress
        ratio = min(1.0, worked / target) if target > 0 else 1.0
        self.progress["maximum"] = 100
        self.progress["value"] = int(ratio * 100)
        self.var_progress.set(f"{int(ratio * 100)}%")

        # Milestone (always shown; assumes you're working when checking)
        self._set_milestone_message(worked=worked, target=target, now_dt=now_dt)

    def copy_summary(self):
        now_dt = datetime.now().replace(microsecond=0)
        schedule, val_msgs = self._collect_schedule()

        try:
            schedule.target_seconds = TimeParser.parse_duration(self.var_target.get())
        except Exception:
            schedule.target_seconds = 8 * 3600 + 30 * 60

        worked = 0
        if not val_msgs:
            try:
                worked = schedule.total_worked_seconds(now_dt)
            except Exception:
                worked = 0

        target = schedule.target_seconds
        remaining = max(0, target - worked)
        overtime = max(0, worked - target)

        lines = []
        lines.append(f"Date: {schedule.on_date.isoformat()}")
        lines.append(f"Now: {now_dt.strftime('%H:%M:%S')}")
        lines.append(f"Target: {TimeParser.format_hms(target)}")
        lines.append("Intervals:")
        for row in self.rows:
            s = row.var_start.get().strip()
            e = row.var_end.get().strip() or "(open)"
            if s or (e and e != "(open)"):
                lines.append(f"  - {s} → {e}")
        if val_msgs:
            lines.append("Validation: " + " ; ".join(dict.fromkeys(val_msgs)))
        lines.append(f"Worked: {TimeParser.format_hms(worked)}")
        lines.append(f"Remaining: {TimeParser.format_hms(remaining)}")
        lines.append(f"Overtime: {TimeParser.format_hms(overtime)}")

        # Include milestone message
        if self.var_milestone_1.get():
            lines.append("Milestone:")
            lines.append(f"  {self.var_milestone_1.get()}")
            if self.var_milestone_2.get():
                lines.append(f"  {self.var_milestone_2.get()}")

        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.var_status.set("Summary copied to clipboard.")


def _seconds_to_timedelta(seconds: int):
    # tiny helper (kept separate to avoid importing timedelta explicitly)
    return datetime.fromtimestamp(0) - datetime.fromtimestamp(0) + (datetime.fromtimestamp(seconds) - datetime.fromtimestamp(0))


def main():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        _print_tkinter_display_help(exc)
        raise SystemExit(1)
    try:
        style = ttk.Style()
        if sys.platform == "win32":
            style.theme_use("winnative")
    except Exception:
        pass

    GuiController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
