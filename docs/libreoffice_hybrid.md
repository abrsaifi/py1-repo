# LibreOffice Hybrid Daemon + CLI Guide

This document describes the hybrid approach used by the project: prefer a long-running
LibreOffice UNO daemon for conversions and fall back to the `soffice` CLI when the daemon
or `pyuno` bridge is unavailable.

Environment variables
---------------------

```bash
export LIBREOFFICE_PREFER_DAEMON=1        # 1 = prefer daemon, 0 = prefer CLI
export LIBREOFFICE_DAEMON_HOST=localhost  # host where UNO daemon listens
export LIBREOFFICE_DAEMON_PORT=2002       # port where UNO daemon listens
export LIBREOFFICE_SOFFICE_PATH=/usr/bin/soffice  # optional override
```

Systemd unit example
---------------------

See `deployment/libreoffice-daemon.service` for a ready-to-use unit file. Summary:

```ini
[Unit]
Description=LibreOffice Headless Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/soffice --headless --accept="socket,host=0.0.0.0,port=2002;urp;" --norestore --nofirststartwizard
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Docker Compose example
----------------------

See `docker/libreoffice-daemon-compose.yml` for a composer snippet. Example command to run:

```bash
docker compose -f docker/libreoffice-daemon-compose.yml up -d
```

Healthchecks
------------

Simple TCP probe against the UNO port is sufficient. For example:

```bash
timeout 1 bash -c "</dev/tcp/127.0.0.1/2002" || exit 1
```

Testing the hybrid implementation
---------------------------------

- Unit tests in `tests/test_document_conversion_hybrid.py` mock both CLI and UNO paths.
- If `pyuno` is not installed, the code will fall back to CLI automatically.

Troubleshooting
---------------

- If UNO conversions fail, set `LIBREOFFICE_PREFER_DAEMON=0` to force CLI mode and check logs.
- Ensure the UNO daemon user has write permissions to configured output directories.

References
----------

- https://wiki.documentfoundation.org/Development/Headless
- https://api.libreoffice.org/docs/pyuno/
