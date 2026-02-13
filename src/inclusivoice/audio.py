from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioChunk:
    pcm: bytes
    timestamp: float


class AudioCaptureService:
    """
    Prototype audio capture service.
    In production, replace simulated chunks with WASAPI loopback capture.
    """

    def __init__(self, chunk_seconds: float = 0.5, max_queue_size: int = 64) -> None:
        self.chunk_seconds = chunk_seconds
        self.output: "queue.Queue[AudioChunk]" = queue.Queue(maxsize=max_queue_size)
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._produce_chunks, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _produce_chunks(self) -> None:
        while self._running:
            # Silence placeholder chunk; swap with real PCM frames in production.
            chunk = AudioChunk(pcm=b"", timestamp=time.time())
            if self.output.full():
                # Keep freshest data by dropping the oldest buffered chunk.
                self.output.get_nowait()
            self.output.put_nowait(chunk)
            time.sleep(self.chunk_seconds)
