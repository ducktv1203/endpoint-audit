import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

from log_cleanup import cleanup_logs_by_size


STORAGE_DIR = Path("storage")


def ensure_storage_dir() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def session_filename() -> Path:
    ensure_storage_dir()
    return STORAGE_DIR / f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"


@dataclass
class SessionStats:
    keys: int = 0
    left_clicks: int = 0
    middle_clicks: int = 0
    right_clicks: int = 0
    wheel_events: int = 0


class InAppInputLogger(tk.Tk):
    """
    Consent-based input logger demo.

    This app only records keyboard/mouse events delivered to THIS window (i.e., while focused).
    It does not install global hooks and does not monitor clipboard.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("In-app Input Logger (Demo)")
        self.geometry("780x520")

        self._recording = False
        self._start_time: datetime | None = None
        self._stats = SessionStats()
        self._session_path: Path | None = None

        self._build_ui()
        self._bind_events()

    def _build_ui(self) -> None:
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.status_var = tk.StringVar(value="Status: Idle (not recording)")
        tk.Label(header, textvariable=self.status_var).pack(side=tk.LEFT)

        btns = tk.Frame(header)
        btns.pack(side=tk.RIGHT)
        tk.Button(btns, text="Start", width=10, command=self.start_recording).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btns, text="Stop", width=10, command=self.stop_recording).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btns, text="Open storage folder", command=self.open_storage).pack(side=tk.LEFT)

        notice = (
            "This demo records only events that occur while this window is focused.\n"
            "Click inside the window, then type/click/scroll to see events appear below."
        )
        tk.Label(self, text=notice, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 8))

        self.log = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20)
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.log.configure(state=tk.DISABLED)

        footer = tk.Frame(self)
        footer.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(footer, text="Clear", width=10, command=self.clear_view).pack(side=tk.LEFT)
        tk.Button(footer, text="Save snapshot", width=12, command=self.save_snapshot).pack(side=tk.LEFT, padx=(6, 0))
        self.stats_var = tk.StringVar(value=self._stats_text())
        tk.Label(footer, textvariable=self.stats_var, anchor=tk.E).pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def _bind_events(self) -> None:
        self.bind("<KeyPress>", self._on_keypress)
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-2>", self._on_middle_click)
        self.bind("<Button-3>", self._on_right_click)
        self.bind("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        self.bind("<Button-4>", self._on_wheel_up)  # Linux
        self.bind("<Button-5>", self._on_wheel_down)  # Linux

    def _append(self, line: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, line + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _stats_text(self) -> str:
        s = self._stats
        return (
            f"Keys: {s.keys} | Left: {s.left_clicks} | Middle: {s.middle_clicks} | "
            f"Right: {s.right_clicks} | Wheel: {s.wheel_events}"
        )

    def _update_stats(self) -> None:
        self.stats_var.set(self._stats_text())

    def start_recording(self) -> None:
        if self._recording:
            return

        self._recording = True
        self._start_time = datetime.now()
        self._stats = SessionStats()
        self._session_path = session_filename()
        self.status_var.set(f"Status: Recording (saving to {self._session_path.as_posix()})")
        self._append(f"[{now_stamp()}] Recording started")
        self._update_stats()

    def stop_recording(self) -> None:
        if not self._recording:
            return

        self._recording = False
        end_time = datetime.now()
        start_time = self._start_time
        self.status_var.set("Status: Idle (not recording)")
        self._append(f"[{now_stamp()}] Recording stopped")

        if self._session_path and start_time:
            self._append("--- Session summary ---")
            self._append(f"Start: {start_time.isoformat(sep=' ', timespec='seconds')}")
            self._append(f"End:   {end_time.isoformat(sep=' ', timespec='seconds')}")
            self._append(self._stats_text())
            self._append("-----------------------")

            self._write_to_file(self._session_path, self._get_view_text())
            cleanup_logs_by_size(directory=STORAGE_DIR, max_size_mb=50)
            messagebox.showinfo("Saved", f"Session saved to:\n{self._session_path}")

    def _get_view_text(self) -> str:
        return self.log.get("1.0", tk.END).rstrip("\n")

    def _write_to_file(self, path: Path, text: str) -> None:
        ensure_storage_dir()
        path.write_text(text + "\n", encoding="utf-8")

    def save_snapshot(self) -> None:
        path = session_filename()
        self._write_to_file(path, self._get_view_text())
        cleanup_logs_by_size(directory=STORAGE_DIR, max_size_mb=50)
        messagebox.showinfo("Saved", f"Snapshot saved to:\n{path}")

    def clear_view(self) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.configure(state=tk.DISABLED)

    def open_storage(self) -> None:
        ensure_storage_dir()
        try:
            os.startfile(str(STORAGE_DIR.resolve()))  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror("Error", f"Could not open storage folder:\n{e}")

    def _should_log(self) -> bool:
        return self._recording

    def _on_keypress(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.keys += 1
        key = event.keysym
        self._append(f"[{now_stamp()}] KEY {key}")
        self._update_stats()

    def _on_left_click(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.left_clicks += 1
        self._append(f"[{now_stamp()}] MOUSE LEFT ({event.x}, {event.y})")
        self._update_stats()

    def _on_middle_click(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.middle_clicks += 1
        self._append(f"[{now_stamp()}] MOUSE MIDDLE ({event.x}, {event.y})")
        self._update_stats()

    def _on_right_click(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.right_clicks += 1
        self._append(f"[{now_stamp()}] MOUSE RIGHT ({event.x}, {event.y})")
        self._update_stats()

    def _on_mousewheel(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.wheel_events += 1
        direction = "UP" if getattr(event, "delta", 0) > 0 else "DOWN"
        self._append(f"[{now_stamp()}] WHEEL {direction}")
        self._update_stats()

    def _on_wheel_up(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.wheel_events += 1
        self._append(f"[{now_stamp()}] WHEEL UP")
        self._update_stats()

    def _on_wheel_down(self, event: tk.Event) -> None:
        if not self._should_log():
            return
        self._stats.wheel_events += 1
        self._append(f"[{now_stamp()}] WHEEL DOWN")
        self._update_stats()


def main() -> None:
    ensure_storage_dir()
    app = InAppInputLogger()
    app.mainloop()


if __name__ == "__main__":
    main()

