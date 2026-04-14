from typing import Annotated as A, TypeVar

from ophyd_async.core import (
    AsyncMovable,
    AsyncStatus,
    SignalR,
    SignalRW,
    StandardReadable,
    StandardReadableFormat as Format,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from .enums import Frequency, StTrg

T_co = TypeVar("T_co", covariant=True)


class FrequencySwitch(EpicsDevice, StandardReadable, AsyncMovable):
    frq: A[SignalRW[Frequency], PvSuffix("selTrgSR"), Format.UNCACHED_SIGNAL]
    busy: A[SignalR[StTrg], PvSuffix("seqTrgSRbusy"), Format.UNCACHED_SIGNAL]

    @AsyncStatus.wrap
    async def set(self, value: T_co) -> AsyncStatus:
        freq = Frequency.from_value(value)
        await self.frq.set(freq)
