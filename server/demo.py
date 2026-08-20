"""
Demo mode.

The public deployment has no agents reporting to it, and Render's free
tier gives the service an ephemeral filesystem, so the SQLite database
is wiped on every restart. A visitor therefore lands on an empty
dashboard, which shows less than no demo at all.

This module fills that gap: on startup it seeds three simulated hosts
with a day of history, then appends a fresh reading every interval so
the page stays live while someone is looking at it.

It is off unless DEMO_MODE=true, so a real deployment with real agents
never touches it. The dashboard shows a banner whenever it is on --
simulated data presented as real would be worse than an empty page.
"""
from __future__ import annotations

import logging
import math
import os
import random
import threading
import time
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)

GB = 1024 ** 3

# Three hosts with different characters, so the dashboard shows contrast
# rather than three copies of the same line.
PROFILES = [
    {
        "agent_id": "demo-web-01",
        "agent_name": "web-01 (demo)",
        "cpu_base": 34.0, "cpu_swing": 18.0, "cpu_noise": 6.0,
        "mem_base": 61.0, "mem_noise": 3.0,
        "disk_total": 120 * GB, "disk_pct": 47.0,
        "mem_total": 8 * GB,
    },
    {
        "agent_id": "demo-db-01",
        "agent_name": "db-01 (demo)",
        "cpu_base": 52.0, "cpu_swing": 12.0, "cpu_noise": 9.0,
        "mem_base": 78.0, "mem_noise": 2.5,
        "disk_total": 500 * GB, "disk_pct": 71.0,
        "mem_total": 32 * GB,
    },
    {
        "agent_id": "demo-worker-01",
        "agent_name": "worker-01 (demo)",
        "cpu_base": 22.0, "cpu_swing": 26.0, "cpu_noise": 12.0,
        "mem_base": 44.0, "mem_noise": 4.0,
        "disk_total": 250 * GB, "disk_pct": 33.0,
        "mem_total": 16 * GB,
    },
]

HISTORY_HOURS = 24
HISTORY_STEP_MINUTES = 5
DEFAULT_INTERVAL_SECONDS = 60


def _clamp(value: float, low: float = 0.5, high: float = 99.5) -> float:
    return max(low, min(high, value))


def _cpu_at(profile: dict, when: datetime, drift: float) -> float:
    """
    Diurnal load curve plus noise plus a slow random walk.

    A flat random series looks obviously fake on a chart. Real servers
    have a daily rhythm, so the sine term is what makes the demo read as
    plausible at a glance.
    """
    hour = when.hour + when.minute / 60
    daily = math.sin((hour - 4) / 24 * 2 * math.pi)   # trough around 4am
    value = (profile["cpu_base"]
             + profile["cpu_swing"] * daily
             + random.gauss(0, profile["cpu_noise"])
             + drift)
    return round(_clamp(value), 1)


def _memory_at(profile: dict, drift: float) -> float:
    value = profile["mem_base"] + random.gauss(0, profile["mem_noise"]) + drift
    return round(_clamp(value, 5.0, 97.0), 1)


def _make_metric(SystemMetric, profile: dict, when: datetime,
                 cpu_drift: float, mem_drift: float):
    mem_pct = _memory_at(profile, mem_drift)
    disk_pct = profile["disk_pct"]
    return SystemMetric(
        agent_id=profile["agent_id"],
        timestamp=when,
        cpu_percent=_cpu_at(profile, when, cpu_drift),
        memory_total=profile["mem_total"],
        memory_used=int(profile["mem_total"] * mem_pct / 100),
        memory_percent=mem_pct,
        disk_total=profile["disk_total"],
        disk_used=int(profile["disk_total"] * disk_pct / 100),
        disk_percent=round(disk_pct, 1),
    )


def _seed_history(app, db, Agent, SystemMetric) -> None:
    """Create the agents and backfill HISTORY_HOURS of readings."""
    with app.app_context():
        now = datetime.now(timezone.utc)

        for profile in PROFILES:
            agent = Agent.query.filter_by(agent_id=profile["agent_id"]).first()
            if agent is None:
                agent = Agent(agent_id=profile["agent_id"],
                              agent_name=profile["agent_name"])
                db.session.add(agent)
            agent.status = "active"
            agent.last_seen = now

            existing = SystemMetric.query.filter_by(
                agent_id=profile["agent_id"]).count()
            if existing:
                continue    # already seeded this boot

            # Walk backwards so the drift accumulates in time order
            points = HISTORY_HOURS * 60 // HISTORY_STEP_MINUTES
            cpu_drift = mem_drift = 0.0
            rows = []
            for i in range(points, 0, -1):
                when = now - timedelta(minutes=i * HISTORY_STEP_MINUTES)
                cpu_drift = _clamp(cpu_drift + random.gauss(0, 0.8), -12, 12)
                mem_drift = _clamp(mem_drift + random.gauss(0, 0.3), -6, 6)
                rows.append(_make_metric(SystemMetric, profile, when,
                                         cpu_drift, mem_drift))
            db.session.bulk_save_objects(rows)

        db.session.commit()
        log.info("demo: seeded %d hosts with %dh of history",
                 len(PROFILES), HISTORY_HOURS)


def _tick(app, db, Agent, SystemMetric, drifts: dict) -> None:
    """Append one fresh reading per host."""
    with app.app_context():
        now = datetime.now(timezone.utc)
        for profile in PROFILES:
            key = profile["agent_id"]
            cpu_drift, mem_drift = drifts[key]
            cpu_drift = _clamp(cpu_drift + random.gauss(0, 0.8), -12, 12)
            mem_drift = _clamp(mem_drift + random.gauss(0, 0.3), -6, 6)
            drifts[key] = (cpu_drift, mem_drift)

            db.session.add(_make_metric(SystemMetric, profile, now,
                                        cpu_drift, mem_drift))

            agent = Agent.query.filter_by(agent_id=key).first()
            if agent:
                agent.last_seen = now
                agent.status = "active"
        db.session.commit()


def _loop(app, db, Agent, SystemMetric, interval: int) -> None:
    drifts = {p["agent_id"]: (0.0, 0.0) for p in PROFILES}
    try:
        _seed_history(app, db, Agent, SystemMetric)
    except Exception:
        log.exception("demo: seeding failed")

    while True:
        time.sleep(interval)
        try:
            _tick(app, db, Agent, SystemMetric, drifts)
        except Exception:
            # One bad tick should not kill the thread and leave the
            # dashboard frozen for the rest of the process's life.
            log.exception("demo: tick failed")


def is_enabled() -> bool:
    return os.getenv("DEMO_MODE", "false").strip().lower() in {"1", "true", "yes"}


def start(app, db, Agent, SystemMetric) -> bool:
    """
    Start the generator in a daemon thread. Returns whether it started.

    Note: with more than one gunicorn worker each worker would run its
    own copy and the hosts would get duplicate readings. The deployment
    runs a single worker, which is all a demo needs.
    """
    if not is_enabled():
        return False

    interval = int(os.getenv("DEMO_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))
    thread = threading.Thread(
        target=_loop, args=(app, db, Agent, SystemMetric, interval),
        name="demo-generator", daemon=True,
    )
    thread.start()
    log.info("demo: generator started, interval %ss", interval)
    return True
