#!/usr/bin/env python3
"""
Dynamic GPU fan curve controller for NVIDIA RTX 3090.
Runs as a daemon, adjusts fan speed based on GPU temperature.

Temperature curve (aggressive):
  < 45°C  → 40%  (idle, quiet)
  45-55°C → 55%  (light load)
  55-65°C → 70%  (moderate)
  65-75°C → 85%  (heavy)
  > 75°C  → 100% (max cooling)

Usage: sudo python3 gpu-fan-curve.py
"""

import logging
import signal
import sys
import time
from pathlib import Path

# Setup logging
log_file = Path("/var/log/gpu-fan-curve.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("gpu-fan-curve")

# Temperature → fan speed curve (sorted ascending by temp)
FAN_CURVE = [
    (45, 40),  # Below 45°C → 40%
    (55, 55),  # 45-55°C   → 55%
    (65, 70),  # 55-65°C   → 70%
    (70, 100),  # >=70°C    → 100%
]

POLL_INTERVAL = 5  # seconds between checks


def get_target_fan(temp: float) -> int:
    """Return target fan speed % for the given temperature."""
    fan = FAN_CURVE[0][1]  # default to lowest
    for threshold, speed in FAN_CURVE:
        if temp >= threshold:
            fan = speed
    return fan


def main():
    from nvitop.api import libnvml as nvml

    running = True

    def handle_signal(signum, frame):
        nonlocal running
        log.info("Received signal %s, shutting down...", signum)
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    nvml.nvmlInit()

    device_count = nvml.nvmlQuery("nvmlDeviceGetCount")
    log.info("Detected %d GPU(s)", device_count)

    handles = []
    for i in range(device_count):
        handle = nvml.nvmlDeviceGetHandleByIndex(i)
        log.info("GPU %d: Setting fan control to MANUAL mode...", i)
        nvml.nvmlQuery(
            "nvmlDeviceSetFanControlPolicy", handle, 0, 1, ignore_errors=False
        )
        handles.append(handle)

    # Print the curve
    log.info("Fan curve:")
    for i, (temp, fan) in enumerate(FAN_CURVE):
        if i == 0:
            log.info("  < %3d°C → %3d%%", temp, fan)
        else:
            prev_temp = FAN_CURVE[i - 1][0]
            log.info("  %3d-%3d°C → %3d%%", prev_temp, temp, fan)

    log.info("Starting fan curve controller (poll every %ds)...", POLL_INTERVAL)
    log.info("Press Ctrl+C or send SIGTERM to stop.")

    prev_fans = {i: -1 for i in range(len(handles))}

    while running:
        try:
            for gpu_idx, handle in enumerate(handles):
                temp = nvml.nvmlQuery("nvmlDeviceGetTemperature", handle, 0)
                fan_speed = nvml.nvmlQuery("nvmlDeviceGetFanSpeed", handle)
                target = get_target_fan(temp)

                if target != prev_fans[gpu_idx]:
                    log.info(
                        "GPU %d | Temp: %3.1f°C | Fan: %3d%% → %3d%% (target)",
                        gpu_idx,
                        temp,
                        fan_speed,
                        target,
                    )
                    nvml.nvmlQuery(
                        "nvmlDeviceSetFanSpeed_v2",
                        handle,
                        0,
                        target,
                        ignore_errors=False,
                    )
                    prev_fans[gpu_idx] = target
                else:
                    log.debug(
                        "GPU %d | Temp: %3.1f°C | Fan: %3d%% (stable)",
                        gpu_idx,
                        temp,
                        fan_speed,
                    )

        except Exception as e:
            log.error("Error: %s", e)

        time.sleep(POLL_INTERVAL)

    log.info("GPU fan curve controller stopped.")


if __name__ == "__main__":
    main()
