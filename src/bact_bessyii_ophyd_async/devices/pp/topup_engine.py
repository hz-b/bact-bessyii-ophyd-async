import asyncio
import itertools

from bluesky.protocols import Stoppable, SyncOrAsync
from ophyd_async.core import AsyncStatus

from ..raw.topup_engine import TopUpEngine as RawTopUpEngine, ToppingUpState, Frequency


class TopUpEngine(RawTopUpEngine, Stoppable):
    def __init__(
        self,
        *args,
        target_current: float,
        acceptable_loss: float,
        requested_injection_frequency: Frequency,
        **kwargs,
    ):

        self.target_current = target_current
        self.acceptable_loss = acceptable_loss
        self.requested_injection_frequency = Frequency(requested_injection_frequency)

        super().__init__(*args, **kwargs)

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
            self.target_current,
            self.acceptable_loss,
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
                f" topup state {value}"
                f" current signal {current_signal.name}"
            )
            return self.state.set(ToppingUpState.OFF)

        try:
            if await self.state.get_value() != ToppingUpState.OFF:
                await self.state.set(ToppingUpState.OFF)
            await self.frequency.set(self.requested_injection_frequency)
            # todo: wait until the TOPUP engine has switched
            #       find out which variable should be checked!
            await asyncio.sleep(10.0)
            await self.state.set(ToppingUpState.ON)
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
