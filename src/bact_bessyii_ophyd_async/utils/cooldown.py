import time
import logging

logger = logging.getLogger("bact-bessy2-ophyd-async")


class Cooldown:
    def __init__(self, *, name:str, delay: float, log=logger):
        self.name = name
        self._delay = delay
        self._last: float | None = None
        self.log =log
        
    def valid(self) -> bool:
        return self._last is not None

    def reset(self):
        self._last = None
        
    def record(self) -> None:
        self._last = time.monotonic()

    def elapsed(self) -> float:
        if self._last is None:
            return float("inf")  # important: no silent fallback
        return time.monotonic() - self._last

    def remaining(self) -> float:
        return max(self._delay - self.elapsed(), 0.0)

    async def wait(self) -> None:
        delay = self.remaining()
        if delay > 0:
            self.log.warning(
                "%s %s need to delay by %s", self.__class__.__name__, self.name, delay
            )
            await asyncio.sleep(delay)
        return time.time() - self._ts

    def __repr__(self) -> str:
        if self._ts is None:
            return f"{self.__class__.__name__}(ts=None)"

        try:
            elapsed = time.monotonic() - self._ts
            return (
                f"{self.__class__.__name__}("
                f"ts={self._ts:.3f}, elapsed={elapsed:.1f}s)"
            )
        except Exception:
            return f"{self.__class__.__name__}(ts={self._ts})"
