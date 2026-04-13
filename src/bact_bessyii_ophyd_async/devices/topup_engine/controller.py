from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Optional

from ophyd_async.core import AsyncStatus


class TopUpController:
    def __init__(
        self,
        *,
        engine: RawTopUpEngine,
        policy: TopUpPolicy,
        cooldown: Cooldown,
        log,
        busy_poll_interval: float = 0.1,
        current_poll_interval: float = 0.2,
        busy_timeout: float = 10.0,
        monitor_timeout: float = 60.0,
    ) -> None:
        self.engine = engine
        self.policy = policy
        self.cooldown = cooldown
        self.log = log

        self.busy_poll_interval = busy_poll_interval
        self.current_poll_interval = current_poll_interval
        self.busy_timeout = busy_timeout
        self.monitor_timeout = monitor_timeout

        self._task: Optional[asyncio.Task] = None

    # =========================================================
    # Public API (called by proxies)
    # =========================================================

    async def start(self) -> None:
        if self._task and not self._task.done():
            self.log.warning("Top-up already running")
            return

        self.log.info("Starting top-up cycle")
        self._task = asyncio.create_task(self._run_cycle())

    async def stop(self) -> None:
        self.log.info("Stopping top-up")

        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

        await self._safe_switch_off()

    async def set_frequency(self, value: Frequency) -> None:
        freq = Frequency.from_value(value)

        self.log.info("Setting frequency to %s", freq)

        await self.cooldown.wait()
        await self._wait_until_not_busy()

        await self.engine.frq_switch.set(freq)

    # =========================================================
    # Core workflow
    # =========================================================

    async def _run_cycle(self) -> None:
        try:
            current = await self.engine.current.get_value()

            if not self.policy.reinjection_required(current):
                self.log.info("No reinjection required (%.3f)", current)
                await self._switch_off()
                return

            await self.cooldown.wait()
            await self._wait_until_not_busy()

            await self._switch_on()

            try:
                await asyncio.wait_for(
                    self._monitor_current(),
                    timeout=self.monitor_timeout,
                )
            except asyncio.TimeoutError:
                self.log.warning("Monitoring timed out")

        except asyncio.CancelledError:
            self.log.info("Top-up cycle cancelled")
            raise

        finally:
            await self._safe_switch_off()

    # =========================================================
    # Internal helpers
    # =========================================================

    async def _wait_until_not_busy(self) -> None:
        async def _loop():
            while True:
                busy = await self.engine.frq_switch.busy.get_value()
                if busy == StTrg.INACTIVE:
                    return
                await asyncio.sleep(self.busy_poll_interval)

        await asyncio.wait_for(_loop(), timeout=self.busy_timeout)

    async def _switch_on(self) -> None:
        self.log.info("Switching ON")
        await self.engine.state.set(ToppingUpState.ON)
        self.cooldown.record()

    async def _switch_off(self) -> None:
        self.log.info("Switching OFF")
        await self.engine.state.set(ToppingUpState.OFF)
        self.cooldown.record()

    async def _safe_switch_off(self) -> None:
        with suppress(Exception):
            await self._switch_off()

    async def _monitor_current(self) -> None:
        while True:
            value = await self.engine.current.get_value()

            if not self.policy.reinjection_required(value):
                self.log.info("Target reached (%.3f)", value)
                return

            await asyncio.sleep(self.current_poll_interval)
