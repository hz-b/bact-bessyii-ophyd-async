import asyncio
import time
import logging

logger = logging.getLogger("bact-bessy2-ophyd-async")


class Cooldown:
    """Wait for the system to cool down

    Records the timestamp on :meth:`record`.

    Cool down can be :meth:`reset`. Then the
    last time stamp is cleared.

    Warning:
        will return
    """
    def __init__(self, *, name:str, delay: float, log=logger):
        self.name = name
        self._delay = delay
        self._last: float | None = None
        self.log =log
        
    def valid(self) -> bool:
        """Check if last time stamp was recorded

        The cool down can be reset. Then the time sta
        """
        return self._last is not None

    def reset(self):
        """clear current time stamp

        Useful if cool down is not valid any more (e.g. using
        device is not in state that it can cool down)
        """
        self._last = None
        
    def record(self) -> None:
        """record current timestamp"""
        self._last = time.monotonic()

    def elapsed(self) -> float:
        """returns time elapsed since timestamp was recorded

        Warning: if
        """
        if self._last is None:
            # Todo: need to check if a good idea ...
            #       rather record the current time
            #       assuming waiting the full delay is enough
            self.record()
        return time.monotonic() - self._last

    def remaining(self) -> float:
        return max(self._delay - self.elapsed(), 0.0)

    async def wait(self) -> float:
        delay = self.remaining()
        if delay > 0:
            self.log.warning(
                "%s %s need to delay by %s", self.__class__.__name__, self.name, delay
            )
            await asyncio.sleep(delay)
        return time.time() - self._last

    def __repr__(self) -> str:
        if self._last is None:
            return f"{self.__class__.__name__}(ts=None)"

        try:
            elapsed = time.monotonic() - self._last
            return (
                f"{self.__class__.__name__}("
                f"ts={self._last:.3f}, elapsed={elapsed:.1f}s)"
            )
        except Exception:
            return f"{self.__class__.__name__}(ts={self._last})"
