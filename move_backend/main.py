import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from core.logging import configure_logging, get_logger
from routes.analyze import router as analyze_router
from routes.portfolio import router as portfolio_router
from routes.whycard import router as whycard_router
from services.connection_manager import manager
from services.event_store import event_store
from services.price_watcher import price_watcher

configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Background tasks
# ---------------------------------------------------------------------------

async def _heartbeat_loop() -> None:
    """Ping all connected clients every 30s to keep connections alive."""
    while True:
        await asyncio.sleep(30)
        if manager.count > 0:
            await manager.broadcast({"type": "heartbeat", "ts": datetime.utcnow().isoformat()})


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    watcher_task = asyncio.create_task(price_watcher.start(), name="price_watcher")
    heartbeat_task = asyncio.create_task(_heartbeat_loop(), name="heartbeat")
    logger.info("startup=complete background_tasks=2")

    yield  # server is running

    logger.info("shutdown=initiated")
    for task in (watcher_task, heartbeat_task):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    logger.info("shutdown=complete")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Move API",
    description="AI-powered stock movement explanation engine using causal inference.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(analyze_router)
app.include_router(portfolio_router)
app.include_router(whycard_router)


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {
        "status": "ok",
        "version": app.version,
        "ws_clients": manager.count,
        "cached_tickers": list(event_store.get_all().keys()),
    }


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket) -> None:
    """Real-time feed. On connect: sends current event cache. On price trigger:
    broadcasts analysis_update to all connected clients."""
    await manager.connect(websocket)
    try:
        # Send current cache immediately so UI can render without waiting
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Move real-time feed",
            "initial_events": event_store.get_all(),
        })

        # Keep connection alive; handle client pings
        while True:
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("ws=client_disconnected")
    except Exception as exc:
        logger.error("ws=error %s", exc)
    finally:
        await manager.disconnect(websocket)
