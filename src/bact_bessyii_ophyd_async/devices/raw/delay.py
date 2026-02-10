from typing import Annotated as A
from ophyd_async.core import (
    AsyncStatus,
    StandardReadable,
    StandardReadableFormat as Format,
    SignalR,
    SubsetEnum,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix


class DelayState(SubsetEnum):
    OFF = "OFF"
    ON = "ON"


class Delay(EpicsDevice, StandardReadable):
    """Delay of kicker pulse to trigger

    Diagnostic kicker
    """

    # fmt:off
    offset :  A[ SignalR[float]      , PvSuffix("offset"), Format.UNCACHED_SIGNAL ]
    switch :  A[ SignalR[DelayState] , PvSuffix("switch"), Format.UNCACHED_SIGNAL ]
    # fmt:on

    @AsyncStatus.wrap
    async def stage(self):
        assert (
            await self.switch.get_value() == DelayState.ON
        ), f"{self.name}: delay switch {self.switch} is not active"
        return await super().stage()

    @AsyncStatus.wrap
    async def unstage(self):
        return await super().unstage()

    async def set(self, value):
        """
        Todo:
            Find out how to correcty override a method that is
            wrapped with AsyncStatus

            Wait for the task? or do nothing ?
        """
        return self.offset.set(value)
