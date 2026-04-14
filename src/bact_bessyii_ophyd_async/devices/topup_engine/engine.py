import asyncio
from typing import Annotated as A

from ophyd_async.core import AsyncStatus, SignalR, SignalRW, StandardReadable, StandardReadableFormat as Format
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from .enums import StTrg, ToppingUpState
from .frequency_switch import FrequencySwitch


class RawTopUpEngine(EpicsDevice, StandardReadable):
    next_injection:    A[ SignalR[float], PvSuffix("estCntDwnS"), Format.UNCACHED_SIGNAL]
    injection_trigger: A [SignalR[StTrg], PvSuffix("stTrg"), Format.UNCACHED_SIGNAL]

    state:   A[ SignalRW[ ToppingUpState], PvSuffix("state"), Format.UNCACHED_SIGNAL]
    current: A[ SignalR[float], PvSuffix("rdCur"), Format.UNCACHED_SIGNAL]

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.frq_switch = FrequencySwitch(*args, **kwargs)
        super().__init__(*args, **kwargs)

    async def describe(self):
        r, u = await asyncio.gather(super().describe(), self.frq_switch.describe())
        r.update(u)
        return r

    async def read(self):
        r, u = await asyncio.gather(super().read(), self.frq_switch.read())
        r.update(u)
        return r
