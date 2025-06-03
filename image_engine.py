"""
image_engine.py
────────────────────────────────────────────────────────────────────────────
Localiza una imagen (template) en cualquiera de los monitores conectados
utilizando MSS + OpenCV.

CLI
───
$ python image_engine.py imgmacos.png --conf 0.80 --timeout 10

• Si encuentra la imagen, imprime las coordenadas absolutas y sale con código 0.
• Si no la encuentra (timeout o max-attempts), sale con código 1.

Uso programático
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

# ────────────────────────── utilidades internas ──────────────────────────
def _default_log(msg: str) -> None:
    print(time.strftime("%Y-%m-%d | %H:%M:%S"), "|", msg)

def _list_real_monitors() -> List[dict]:
    """Devuelve los descriptores MSS de monitores reales (ignora monitors[0])."""
    with mss.mss() as sct:
        return list(sct.monitors[1:])

def _capture_monitor(mon: dict) -> np.ndarray:
    """Captura un monitor y devuelve un np.ndarray BGR."""
    with mss.mss() as sct:
        grab = sct.grab(mon)            # BGRA
    return cv2.cvtColor(np.array(grab), cv2.COLOR_BGRA2BGR)

def _build_scales(min_scale=0.8, max_scale=1.2, step=0.1) -> List[float]:
    """Genera la lista de escalas: [1.0, 0.9, 1.1, 0.8, 1.2, …]."""
    scales = [1.0]
    k = 1
    while True:
        down = 1.0 - k*step
        up   = 1.0 + k*step
        added = False
        if down >= min_scale - 1e-6:
            scales.append(round(down,2)); added = True
        if up   <= max_scale + 1e-6:
            scales.append(round(up,2)); added = True
        if not added:
            break
        k += 1
    return scales

# ────────────────────────── búsqueda en un solo monitor ──────────────────────────
def _find_in_monitor(
    haystack: np.ndarray,
    template: np.ndarray,
    confs: List[float],
    scales: List[float],
    log_fn: Callable[[str], None],
    attempts_start: int,
    max_attempts: int
) -> Tuple[Optional[Tuple[int,int,int,int]], int]:
    """
    Process a single monitor's capture (haystack) by iterating through
    confidence levels and scale factors. Returns ((x, y, w, h), attempts)
    if a match is found, or (None, attempts) otherwise.
    """
    attempts = attempts_start
    th, tw = template.shape[:2]

    for conf in confs:
        for sc in scales:
            attempts += 1
            if attempts > max_attempts:
                return None, attempts

            # Resize the template according to the current scale
            resized = template if sc == 1.0 else cv2.resize(
                template, (int(tw * sc), int(th * sc)), interpolation=cv2.INTER_AREA
            )

            # Check that the resized template fits within the haystack image
            hay_h, hay_w = haystack.shape[:2]
            templ_h, templ_w = resized.shape[:2]
            if templ_h > hay_h or templ_w > hay_w:
                log_fn(f"⚠️ Skipping scale={sc:.2f} because template ({templ_h}×{templ_w}) > haystack ({hay_h}×{hay_w})")
                continue

            # Perform template matching only if the template fits
            res = cv2.matchTemplate(haystack, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            log_fn(f"[attempt {attempts:02d}] conf≥{conf:.2f} sc={sc:.2f} → {max_val:.3f}")
            if max_val >= conf:
                x, y = max_loc
                h, w = resized.shape[:2]
                return (x, y, w, h), attempts

    return None, attempts

# ───────────────────────────── find_image() ──────────────────────────────
def find_image(
    template_path: str | Path,
    *,
    base_confidence: float = 1.0,
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
    Search `template_path` on all connected monitors. Returns
    (abs_x, abs_y, w, h, monitor_index) if found, or None otherwise.

    - If caller provides `base_confidence` (e.g. from JSON), start exactly
      at that value and decrement by `confidence_step` down to `min_confidence`.
    - If no confidence is provided (uses default 1.0), start at 1.0 and
      step down by `confidence_step` down to `min_confidence`.
    """
    template_path = Path(template_path)
    if not template_path.exists():
        log_fn(f"❌ Template not found: {template_path}")
        return None

    template = cv2.imread(str(template_path))
    if template is None:
        log_fn(f"❌ OpenCV failed to read {template_path}")
        return None

    # Build confidence ladder starting at base_confidence, decrementing by confidence_step
    confs: List[float] = []
    cur_conf = base_confidence
    while cur_conf >= min_confidence - 1e-6:
        confs.append(round(cur_conf, 2))
        cur_conf -= confidence_step

    # Ensure unique and sorted (descending)
    confs = sorted(set(confs), reverse=True)

    # Build scale list [1.0, 0.9, 1.1, 0.8, 1.2, …]
    scales = _build_scales(min_scale, max_scale, scale_step)

    real_mons = _list_real_monitors()
    log_fn(f"🔍 Starting search | base_conf={base_confidence:.2f} "
           f"timeout={'∞' if timeout is None else timeout}s monitors={len(real_mons)}")

    t0 = time.time()

    for mon_idx, mon in enumerate(real_mons, start=1):
        attempts = 0

        # Check overall timeout before processing this monitor
        if timeout is not None and (time.time() - t0) >= timeout:
            log_fn("⏱ Timeout reached before scanning all monitors.")
            return None

        left, top = mon["left"], mon["top"]
        right, bottom = left + mon["width"], top + mon["height"]
        log_fn(f"🔍 Looking in monitor {mon_idx} bounds=({left},{top})..({right},{bottom})")

        hay = _capture_monitor(mon)  # Capture BGR image of this monitor

        # Search within this single monitor
        found, attempts = _find_in_monitor(
            hay, template, confs, scales, log_fn, 0, max_attempts
        )
        if found:
            x_rel, y_rel, w, h = found
            abs_x = left + x_rel
            abs_y = top + y_rel
            log_fn(f"✅ FOUND in monitor {mon_idx} at absolute ({abs_x},{abs_y}) "
                   f"size=({w}×{h})")
            return abs_x, abs_y, w, h, mon_idx

        # Small pause before next monitor
        time.sleep(poll_every)

    log_fn("❌ No match found in any monitor.")
    return None

# ──────────────────────────── CLI helper ────────────────────────────────
def _cli() -> None:
    p = argparse.ArgumentParser(
        description="Locate a template image on all connected monitors.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("template",    help="Path to the template image")
    p.add_argument("--conf",      type=float, default=0.80, help="base confidence")
    p.add_argument("--timeout",   type=float, default=10,   help="seconds (0=∞)")
    p.add_argument("--poll",      type=float, default=0.50, help="sleep between monitors")
    p.add_argument("--max-attempts", type=int, default=20, help="max template attempts")
    args = p.parse_args()

    # **DEBUG**: grab screenshots de cada monitor
    with mss.mss() as sct:
        for idx, mon in enumerate(sct.monitors[1:], start=1):
            img = np.array(sct.grab(mon))
            bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            dbg = f"screen{idx}.png"
            cv2.imwrite(dbg, bgr)
            print(f"🖥 Saved debug screenshot → {dbg}")

    # buscar
    res = find_image(
        args.template,
        base_confidence=args.conf,
        timeout=None if args.timeout<=0 else args.timeout,
        poll_every=args.poll,
        max_attempts=args.max_attempts
    )

    if res:
        x, y, w, h, mon_idx = res
        print(f"\nFOUND at ({x}, {y}) size=({w}×{h}) on monitor {mon_idx}")
        sys.exit(0)

    print("❌ No match found.")
    sys.exit(1)

# ──────────────────────────── punto de entrada ──────────────────────────
if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]!="--help":
        _cli()