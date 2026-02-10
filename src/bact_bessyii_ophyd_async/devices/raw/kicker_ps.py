from typing import Annotated as A
from ophyd_async.core import (
    StandardReadableFormat as Format,
    StandardReadable,
    SignalR,
    SignalRW,
    SubsetEnum,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix


class PoweredState(SubsetEnum):
    OFF = "Power OFF"
    ON = "Power ON"


class HighVoltageState(SubsetEnum):
    OFF = "HV OFF"
    ON = "HV ON"


class KickerPS(EpicsDevice, StandardReadable):
    """Power converter of the kicker

    At least for the diagnostic kicker

    HV requires a bit of time to get data
    """

    # fmt:off
    powered   :  A[ SignalR[PoweredState]     , PvSuffix("stat1")     , Format.UNCACHED_SIGNAL ]
    hv_on     :  A[ SignalR[HighVoltageState] , PvSuffix("stat2")     , Format.UNCACHED_SIGNAL ]

    setpoint  : A[ SignalRW[float]            , PvSuffix("set")       , Format.UNCACHED_SIGNAL ]
    readback  : A[ SignalR[float]             , PvSuffix("rdbk")      , Format.UNCACHED_SIGNAL ]

    units     : A[ SignalR[str]               , PvSuffix("rdbk.EGU")  , Format.UNCACHED_SIGNAL ]
    precision : A[ SignalR[int]               , PvSuffix("rdbk.PREC") , Format.UNCACHED_SIGNAL ]

    # fmt:on
