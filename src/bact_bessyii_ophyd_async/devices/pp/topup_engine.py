import asyncio
import itertools
import time

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
        await self.set_topping_up_off()

    async def set_topping_up_off(self):
        state = await self.state.get_value()
        st = self.state.set(ToppingUpState.OFF)

        if self.timestamped_topup_off is None:
            self.log.warning("Last switch off timestamp was None, thus recording current time")
            self.timestamped_topup_off.record()

        if state == ToppingUpState.ON:
            self.log.warning("topping up state was %s thus recording switch time", repr(state))
            self.timestamped_topup_off.record()
        await st

    def get_timestamp_from_last_off(self) -> float:
        if not self.timestamped_topup_off.valid():
            self.timestamped_topup_off.record()        
            self.log.warning("Using current time as timestamp for last switch as it was not defined")
        return self.timestamped_topup_off.elapsed()
        
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
        if value == ToppingUpState.OFF:
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection requested"
                f" topup state {value}"
                f" current signal {self.current.name}"
            )
            await self.set_topping_up_off()
            return

        if not await self.reinjection_required():
            self.log.warning(
                f"{self.__class__.__name__}: no reinjection required"
                f" topup state {value}"
                f" current signal {self.current.name}"
            )
            await self.set_topping_up_off()
            return

        await asyncio.wait_for(
            frequency_switched(self.frq_switch.busy, self.log), timeout=10.0
        )

        try:
            # Todo: add check that engine can switch!
            st = self.state.set(ToppingUpState.ON)
            self.timestamped_topup_off.reset()
            await st
            await asyncio.wait_for(
                monitor_current(self.current, self.target_current, self.log), timeout=60.0
            )
        finally:
            await self.set_topping_up_off()

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
