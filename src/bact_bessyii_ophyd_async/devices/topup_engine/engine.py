import asyncio
from typing import Annotated as A

from ophyd_async.core import (
    SignalR,
    SignalRW,
    StandardReadable,
    StandardReadableFormat as Format,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from .enums import StTrg, ToppingUpState
from .frequency_switch import FrequencySwitch


class RawTopUpEngine(EpicsDevice, StandardReadable):
    # fmt:off
    next_injection:    A[ SignalR[float] , PvSuffix("estCntDwnS") , Format.UNCACHED_SIGNAL ]
    injection_trigger: A[ SignalR[StTrg] , PvSuffix("stTrg")      , Format.UNCACHED_SIGNAL ]

    state:   A[ SignalRW[ToppingUpState] , PvSuffix("state")      , Format.UNCACHED_SIGNAL ]
    current: A[ SignalR[float]           , PvSuffix("rdCur")      , Format.UNCACHED_SIGNAL ]
    # fmt:on

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.frq_switch = FrequencySwitch(*args, **kwargs)
        super().__init__(*args, **kwargs)


__all__ = ["RawTopUpEngine"]
