"""Local Uvicorn runner for the single Hixton process."""

from __future__ import annotations

import threading
import webbrowser

import uvicorn

from hixton.config import ProjectConfig
from hixton.runtime.supervisor import RuntimeSupervisor
from hixton.ui.api import create_app


def run_local_dashboard(config: ProjectConfig, *, open_browser: bool = True) -> int:
    if config.ui_bind not in {"127.0.0.1", "localhost"}:
        raise ValueError("V1 UI may bind only to localhost")
    supervisor = RuntimeSupervisor(config)
    app = create_app(config, supervisor)
    url = f"http://{config.ui_bind}:{config.ui_port}/"
    if open_browser:
        timer = threading.Timer(1.25, lambda: webbrowser.open(url))
        timer.daemon = True
        timer.start()
    uvicorn.run(
        app,
        host=config.ui_bind,
        port=config.ui_port,
        log_level="info",
        access_log=False,
    )
    return 0
