import asyncio
import itertools

from bluesky.protocols import Stoppable, SyncOrAsync
from ophyd_async.core import AsyncStatus, AsyncMovable

from ..raw.topup_engine import TopUpEngine as RawTopUpEngine, ToppingUpState, StTrg


class TopUpEngine(RawTopUpEngine, AsyncMovable, Stoppable):
    """

    Currently designed to only handle main current
    """
    def __init__(
        self,
        *args,
        target_current: float,
        acceptable_loss: float,
        **kwargs,
    ):

        self.target_current = target_current
        self.acceptable_loss = acceptable_loss

        super().__init__(*args, **kwargs)

    async def stop(self, success=True) -> SyncOrAsync[None]:
        await self.state.set(ToppingUpState.OFF)
        return None

    @AsyncStatus.wrap
    async def set(self, value):
        """

        To be prepared for overloading for using an other signal
        """
        return await self.set_using_signal(
            value,
        )

    async def set_using_signal(
        self,
        value: ToppingUpState,
    ):
        value = ToppingUpState(value)
        if not value:
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection requested"
                f" topup state {value}"
                f" current signal {self.current.name}"
            )
            return await self.state.set(ToppingUpState.OFF)

        assert value

        if not await self.reinjection_required():
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection required"
                f" topup state {value}"
                f" current signal {self.current.name}"
            )
            return self.state.set(ToppingUpState.OFF)

        await asyncio.wait_for(
            frequency_switched(self.frq_switch.busy, self.log), timeout=10.0
        )

        try:
            # Todo: add check that engine can switch!

            await self.state.set(ToppingUpState.ON)
            await asyncio.wait_for(
                monitor_current(self.current, self.target_current, self.log), timeout=60.0
            )
        finally:
            await self.state.set(ToppingUpState.OFF)

    async def reinjection_required(self) -> bool:
        return reinjection_required(
            self.target_current, self.acceptable_loss, await self.current.get_value(), self.log
        )



async def frequency_switched(switch_signal, log):
    counter = itertools.count()
    for cnt in counter:
        value = await switch_signal.get_value()
        if value == StTrg.INACTIVE:
            log.info("No frequency switch active (any more)")
            return cnt


async def monitor_current(current_signal, target_current: float, log):
    counter = itertools.count()
    for cnt in counter:
        value = await current_signal.get_value()
        if value > target_current:
            log.warning("Topup: switch off")
            return cnt


def reinjection_required(
    target_current: float, acceptable_loss: float, actual_current: float, log
) -> bool:
    """ """
    txt = f"{actual_current=}, range: {target_current=} - {acceptable_loss=}"
    if actual_current >= target_current - acceptable_loss:
        log.info(txt + ": sufficient")
        return False
    log.warning(txt + ": insufficient")
    return True
