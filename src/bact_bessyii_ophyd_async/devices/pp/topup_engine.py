import asyncio
import itertools
from typing import Annotated as A

from bluesky.protocols import SyncOrAsync
from ophyd_async.core import SignalR, StandardReadableFormat as Format, AsyncStatus

from ..raw.topup_engine import TopUpEngine as RawTopUpEngine, ToppingUpState, Frequency
from bluesky.protocols import Stoppable, SyncOrAsync


class TopupEngine(RawTopUpEngine, Stoppable):
    # fmt:off
    target_current:  A[SignalR[float], Format.CONFIG_SIGNAL]
    acceptable_loss: A[SignalR[float], Format.CONFIG_SIGNAL]
    # fmt:on
    requested_injection_frequency: A[SignalR[Frequency], Format.CONFIG_SIGNAL]

    async def stop(self, success=True) -> SyncOrAsync[None]:
        await self.state.set(ToppingUpState.OFF)
        return None

    # async def reinjection_required(self):
    #    return await reinjection_required_signal(
    #        self.target_current, self.acceptable_loss, self.current, self.log
    #    )

    @AsyncStatus.wrap
    async def set(self, value):
        """

        To be prepared for overloading for using an other signal
        """
        return await self.set_using_signal(
            await self.target_current.get_value(),
            await self.acceptable_loss.get_value(),
            self.current,
            value,
        )

    async def set_using_signal(
        self,
        target_current: float,
        acceptable_loss: float,
        current_signal,
        value: ToppingUpState,
    ):
        value = ToppingUpState(value)
        if not value:
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection requested"
                f" topup state {value}"
                f" current signal {current_signal.name}"
            )
            return await self.state.set(ToppingUpState.OFF)

        assert value

        if not reinjection_required(
            target_current, acceptable_loss, await current_signal.get_value(), self.log
        ):
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection required"
                f" topup state {value} "
                f"current signal {current_signal.name}"
            )
            return self.state.set(ToppingUpState.OFF)

        try:
            await self.state.set(ToppingUpState.ON)
            await self.frequency.set(
                await self.requested_injection_frequency.get_value()
            )
            await asyncio.wait_for(
                monitor_current(current_signal, target_current, self.log), timeout=60.0
            )
        finally:
            await self.state.set(ToppingUpState.OFF)


async def monitor_current(current_signal, target_current: float, log):
    counter = itertools.count()
    for cnt in counter:
        value = await current_signal.get_value()
        if value > target_current:
            log.warning(f"Topup: switch off")
            return cnt


def reinjection_required(
    target_current: float, acceptable_loss: float, actual_current: float, log
):
    """ """
    tc = target_current
    loss = acceptable_loss
    cur = actual_current

    txt = f"actual current {cur}, range: target {tc} - loss {loss}"
    if cur >= tc - loss:
        log.info(txt + " sufficient")
        return False
    log.warning(txt + " insufficient")
    return True
