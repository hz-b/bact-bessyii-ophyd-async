from typing import Annotated as A, TypeVar

from ophyd_async.core import AsyncMovable, AsyncStatus, SignalR, SignalRW, StandardReadable
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from .enums import Frequency, StTrg

T_co = TypeVar("T_co", covariant=True)


class FrequencySwitch(EpicsDevice, StandardReadable, AsyncMovable):
    frq: A[SignalRW[Frequency], PvSuffix("selTrgSR")]
    busy: A[SignalR[StTrg], PvSuffix("seqTrgSRbusy")]

    @AsyncStatus.wrap
    async def set(self, value: T_co) -> AsyncStatus:
        freq = Frequency.from_value(value)
        await self.frq.set(freq)
