import threading
import time
import os
import shutil


def start_cleanup_thread(upload_dir, retention_seconds=24 * 3600, interval_seconds=3600):
    """Start a background thread that removes upload dirs older than retention_seconds.

    This is a conservative helper that can be used by the new app structure while
    we migrate logic from `server.py`.
    """
    def _worker():
        while True:
            try:
                now = time.time()
                for name in os.listdir(upload_dir):
                    path = os.path.join(upload_dir, name)
                    try:
                        mtime = os.path.getmtime(path)
                        if now - mtime > retention_seconds:
                            shutil.rmtree(path, ignore_errors=True)
                    except Exception:
                        pass
            except Exception:
                pass
            time.sleep(interval_seconds)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t
