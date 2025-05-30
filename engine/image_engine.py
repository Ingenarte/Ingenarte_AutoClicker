"""
image_engine.py
────────────────────────────────────────────────────────────────────────────
Locate a template image on *any* monitor using MSS + OpenCV,
with per-monitor Retina/HiDPI scaling correction.

Usage (CLI)
───────────
$ python image_engine.py imgmacos.png --conf 0.80 --timeout 10

• If found: prints logical coords and exits 0.
• If not: exits 1.

Programmatic API
────────────────
from image_engine import find_image

loc = find_image("imgmacos.png", base_confidence=0.80, timeout=10)
if loc:
    x, y, w, h, mon_idx = loc
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Callable, Optional, Tuple, List

import cv2
import mss
import numpy as np

# ────────────────────────── Helpers ──────────────────────────

def _default_log(msg: str) -> None:
    print(time.strftime("%Y-%m-%d | %H:%M:%S"), "|", msg)

def _list_real_monitors() -> List[dict]:
    """Return MSS descriptors for each real monitor (skip the stitched virtual)."""
    with mss.mss() as sct:
        return list(sct.monitors[1:])

def _capture_monitor(mon: dict) -> np.ndarray:
    """Capture one monitor and return a BGR numpy array (physical pixels)."""
    with mss.mss() as sct:
        shot = sct.grab(mon)  # BGRA
    return cv2.cvtColor(np.array(shot), cv2.COLOR_BGRA2BGR)

def _build_scales(min_scale=0.8, max_scale=1.2, step=0.1) -> List[float]:
    """Generate [1.0, 0.9, 1.1, 0.8, 1.2,…] around 1.0."""
    scales = [1.0]
    k = 1
    while True:
        down = 1.0 - k * step
        up   = 1.0 + k * step
        added = False
        if down >= min_scale - 1e-6:
            scales.append(round(down, 2)); added = True
        if up <= max_scale + 1e-6:
            scales.append(round(up,   2)); added = True
        if not added:
            break
        k += 1
    return scales

# ────────────────────────── Core API ──────────────────────────

def find_image(
    template_path: str|Path,
    *,
    base_confidence: float = 0.80,
    timeout: Optional[float] = 10.0,
    poll_every: float = 0.50,
    max_attempts: int = 20,
    min_confidence: float = 0.30,
    confidence_step: float = 0.05,
    min_scale: float = 0.80,
    max_scale: float = 1.20,
    scale_step: float = 0.10,
    log_fn: Callable[[str], None] = _default_log,
) -> Optional[Tuple[int,int,int,int,int]]:
    """
    Search `template_path` on every real monitor.
    Returns (x_logical, y_logical, w_logical, h_logical, monitor_index) or None.
    """
    tp = Path(template_path)
    if not tp.exists():
        log_fn(f"❌ Template not found: {tp}")
        return None
    template = cv2.imread(str(tp))
    if template is None:
        log_fn(f"❌ Could not load template: {tp}")
        return None

    # Build confidence ladder
    confs: List[float] = []
    cur = 0.95
    while cur >= min_confidence - 1e-6:
        confs.append(round(cur, 2))
        cur -= confidence_step
    if base_confidence not in confs:
        confs.append(base_confidence)
    confs = sorted(set(confs), reverse=True)

    scales = _build_scales(min_scale, max_scale, scale_step)
    monitors = _list_real_monitors()

    log_fn(f"🔍 Searching  base_conf={base_confidence:.2f} "
           f"timeout={'∞' if timeout is None else timeout}s  monitors={len(monitors)}")

    start_time = time.time()
    # Loop per monitor
    for midx, mon in enumerate(monitors, start=1):
        left_pt, top_pt = mon["left"], mon["top"]
        w_pt, h_pt      = mon["width"], mon["height"]

        # 1) grab physical buffer & compute per-monitor scale
        hay = _capture_monitor(mon)
        h_px, w_px = hay.shape[:2]
        scale_x_mon = w_px / w_pt
        scale_y_mon = h_px / h_pt

        log_fn(f"🔍 Monitor {midx}  logical_bounds=({left_pt},{top_pt}).."
               f"({left_pt+w_pt},{top_pt+h_pt})  "
               f"physical_size=({w_px}×{h_px})  scale=({scale_x_mon:.2f},{scale_y_mon:.2f})")

        attempts = 0
        # search ladder
        for conf in confs:
            for sc in scales:
                if attempts >= max_attempts:
                    log_fn("🔚 Reached max_attempts on this monitor, moving on.")
                    break
                attempts += 1

                th, tw = template.shape[:2]
                tpl = (template if sc == 1.0
                       else cv2.resize(template,
                                       (int(tw*sc), int(th*sc)),
                                       interpolation=cv2.INTER_AREA))

                res = cv2.matchTemplate(hay, tpl, cv2.TM_CCOEFF_NORMED)
                _, mv, _, ml = cv2.minMaxLoc(res)
                log_fn(f"[{attempts:02d}] conf≥{conf:.2f} sc={sc:.2f} → {mv:.3f}")

                if mv >= conf:
                    # ml is in *physical* pixels
                    phys_x = left_pt  * scale_x_mon + ml[0]
                    phys_y = top_pt   * scale_y_mon + ml[1]
                    ph_h, ph_w = tpl.shape[:2]

                    log_fn(f"✅ FOUND mon{midx} phys=({int(phys_x)},{int(phys_y)}) "
                           f"conf={mv:.3f} sc={sc:.2f}")

                    # convert back to logical (points)
                    x_log = int(phys_x / scale_x_mon)
                    y_log = int(phys_y / scale_y_mon)
                    w_log = int(ph_w   / scale_x_mon)
                    h_log = int(ph_h   / scale_y_mon)

                    log_fn(f"➡ logical=({x_log},{y_log}) size=({w_log}×{h_log})")
                    return x_log, y_log, w_log, h_log, midx

            if attempts >= max_attempts:
                break

        # inter-monitor wait & timeout check
        time.sleep(poll_every)
        if timeout is not None and time.time() - start_time >= timeout:
            log_fn("⏱ Timeout reached; aborting search.")
            return None

    log_fn("❌ No match found on any monitor.")
    return None

# ────────────────────────── CLI Entry ──────────────────────────

def _cli() -> None:
    p = argparse.ArgumentParser(
        description="Locate a template across all monitors",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("template", help="Path to the template image")
    p.add_argument("--conf",    type=float, default=0.80, help="Base confidence")
    p.add_argument("--timeout", type=float, default=10,   help="Timeout in s (0=∞)")
    p.add_argument("--poll",    type=float, default=0.50, help="Seconds between polls")
    args = p.parse_args()

    # Debug: save each monitor as screenN.png
    with mss.mss() as sct:
        for idx, m in enumerate(sct.monitors[1:], start=1):
            img = np.array(sct.grab(m))
            bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            fn = f"screen{idx}.png"
            cv2.imwrite(fn, bgr)
            print(f"🖥 Saved debug screenshot → {fn}")

    loc = find_image(
        args.template,
        base_confidence=args.conf,
        timeout=None if args.timeout <= 0 else args.timeout,
        poll_every=args.poll,
    )
    if loc:
        x, y, w, h, midx = loc
        print(f"\nFOUND at ({x},{y}) size=({w}×{h}) on monitor {midx}")
        # summarize monitor bounds
        with mss.mss() as sct:
            for idx, m in enumerate(sct.monitors[1:], start=1):
                l, t = m["left"], m["top"]
                r, b = l + m["width"], t + m["height"]
                tag = "👈 HERE" if idx == midx else ""
                print(f"Monitor {idx} → ({l},{t})..({r},{b}) {tag}")
        sys.exit(0)

    print("❌ No match found.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--help":
        _cli()