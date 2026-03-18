from __future__ import annotations

from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class ProcInfo:
    pid: int
    name: str
    exe: str | None


def snapshot_processes() -> dict[int, ProcInfo]:
    procs: dict[int, ProcInfo] = {}
    for p in psutil.process_iter(attrs=["pid", "name", "exe"]):
        try:
            info = p.info
            procs[int(info["pid"])] = ProcInfo(
                pid=int(info["pid"]),
                name=str(info.get("name") or ""),
                exe=str(info.get("exe")) if info.get("exe") else None,
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def diff_processes(
    prev: dict[int, ProcInfo], curr: dict[int, ProcInfo]
) -> tuple[list[ProcInfo], list[ProcInfo]]:
    started: list[ProcInfo] = []
    stopped: list[ProcInfo] = []

    prev_pids = set(prev.keys())
    curr_pids = set(curr.keys())

    for pid in curr_pids - prev_pids:
        started.append(curr[pid])
    for pid in prev_pids - curr_pids:
        stopped.append(prev[pid])

    return started, stopped

