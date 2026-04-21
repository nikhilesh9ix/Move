from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import WebSocket
from core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Tracks active WebSocket connections and broadcasts JSON messages.

    Silently cleans up dead connections on each broadcast.
    Module singleton is `manager`.
    """

    def __init__(self) -> None:
        self._connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.append(ws)
        logger.info("ws=connect total_clients=%d", len(self._connections))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            if ws in self._connections:
                self._connections.remove(ws)
        logger.info("ws=disconnect total_clients=%d", len(self._connections))

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Send message to all connected clients; remove any that have closed."""
        if not self._connections:
            return

        async with self._lock:
            snapshot = list(self._connections)

        dead: List[WebSocket] = []
        for ws in snapshot:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self._connections:
                        self._connections.remove(ws)
            logger.info("ws=cleaned_dead count=%d remaining=%d", len(dead), len(self._connections))

    @property
    def count(self) -> int:
        return len(self._connections)


# Module-level singleton
manager = ConnectionManager()
