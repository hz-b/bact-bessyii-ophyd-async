from enum import Enum
from typing import Annotated as A


from ophyd_async.core import StandardReadableFormat as Format, StandardReadable, SignalR, SignalRW, StrictEnum, \
    SubsetEnum
from ophyd_async.epics.core import EpicsDevice, PvSuffix


class ToppingUpState(SubsetEnum):
    OFF = "TopUp Automatic OFF"
    ON = "TopUp Automatic ON"


class StTrg(SubsetEnum):
    INACTIVE = "inactive"
    ACTIVE = "active"


class Frequency(SubsetEnum):
    ONE_HZ = "1 Hz"
    HALF_HZ = "0.5 Hz"
    TENTH_HZ = "0.1 Hz"


class TopUpEngine(EpicsDevice, StandardReadable):
    next_injection    : A[ SignalR[float], PvSuffix("estCntDwnS"),  Format.UNCACHED_SIGNAL  ]
    injection_trigger : A[ SignalR[StTrg], PvSuffix("stTrg"),  Format.UNCACHED_SIGNAL  ]
    number_of_bunches : A[ SignalR[int], PvSuffix("setMaxNrBunches"),  Format.UNCACHED_SIGNAL ]
    state      : A[ SignalRW[ToppingUpState] , PvSuffix( "state"    ), Format.UNCACHED_SIGNAL ]
    current    : A[ SignalR[float]           , PvSuffix( "rdCur"    ), Format.UNCACHED_SIGNAL ]
    sb_current : A[ SignalR[float]           , PvSuffix( "rdCurCS"  ), Format.UNCACHED_SIGNAL ]
    frequency  : A[ SignalR[Frequency]       , PvSuffix( "selTrgSR" ), Format.UNCACHED_SIGNAL ]


