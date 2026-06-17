# nvfan

GPU fan curve controller for NVIDIA. Runs as a systemd service, adjusts fan speed based on GPU temperature.

```
< 45°C  → 40%    (idle)
45–55°C → 55%    (light load)
55–65°C → 70%    (moderate)
≥ 70°C  → 100%   (max cooling)
```

## Quick start

```bash
./build.sh          # compile standalone binary
sudo dpkg -i nvfan_1.0.0_amd64.deb   # install + enable service
```

Or manually:

```bash
sudo ./nvfan            # run directly
sudo journalctl -u nvfan  # logs (when running as service)
```

## Build

**Requirements:**

- Python 3.14
- gcc, scons, libpython3.14-dev (system packages)
- nuitka (`pip install nuitka`)
- nvitop (`pip install nvitop`) — pulls in psutil, nvidia-ml-py

```bash
./build.sh           # → nvfan (standalone onefile binary, ~11 MB)
./make-deb.sh        # → nvfan_1.0.0_amd64.deb
```

The binary ships Python runtime and all dependencies (nvitop, psutil, pynvml) bundled inside. Only `glibc` and `libnvml.so` (from NVIDIA driver) are needed at runtime.

## Structure

| File | Description |
|---|---|
| `gpu-fan-curve.py` | Source — the daemon |
| `build.sh` | Build standalone binary |
| `make-deb.sh` | Build DEB package |
| `nvfan.service` | systemd unit file |
| `debian/` | DEB control, postinst, prerm |

## DEB package

`make-deb.sh` creates `nvfan_1.0.0_amd64.deb` which installs:

- `/usr/local/bin/nvfan` — binary
- `/etc/systemd/system/nvfan.service` — service
- auto-enables and starts the service on install

## License

MIT