from typing import Annotated as A

from ophyd_async.core import AsyncStatus, SignalR, SignalRW, StandardReadable
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from .enums import StTrg, ToppingUpState
from .frequency_switch import FrequencySwitch


class RawTopUpEngine(EpicsDevice, StandardReadable):
    next_injection: A[SignalR[float], PvSuffix("estCntDwnS")]
    injection_trigger: A[SignalR[StTrg], PvSuffix("stTrg")]

    state: A[SignalRW[ToppingUpState], PvSuffix("state")]
    current: A[SignalR[float], PvSuffix("rdCur")]

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.frq_switch = FrequencySwitch(*args, **kwargs)
        super().__init__(*args, **kwargs)
