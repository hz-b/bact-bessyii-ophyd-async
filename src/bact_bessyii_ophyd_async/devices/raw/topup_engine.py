import logging
from typing import Annotated as A, Union
from math import isclose

from bluesky.protocols import T_co
from ophyd_async.core import (
    AsyncMovable,
    StandardReadableFormat as Format,
    StandardReadable,
    SignalR,
    SignalRW,
    SubsetEnum,
    AsyncStatus,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix

logger = logging.getLogger("bact-bessyii-ophyd-async")


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

    @classmethod
    def from_value(cls, value: Union["Frequency", float]):
        if isinstance(value, cls):
            return value

            # Reject strings explicitly
        if isinstance(value, str):
            raise ValueError(
                f"String inputs (like {value}) are not accepted by"
                " Frequency.from_value; pass a numeric value (int/float)"
                " or a Frequency member."
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{value!r} is not a valid Frequency or numeric value")

        mapping = {
            1.0: cls.ONE_HZ,
            0.5: cls.HALF_HZ,
            0.1: cls.TENTH_HZ,
        }

        for expected, freq in mapping.items():
            if isclose(numeric, expected, rel_tol=0.0, abs_tol=1e-9):
                return freq

        raise ValueError(f"{numeric} Hz is not supported (allowed: 1.0, 0.5, 0.1 Hz)")


class FrequencySwitch(EpicsDevice, StandardReadable, AsyncMovable):
    """Frequency switch only made if not in injection state

    Will raise an assertion error if topup engine is in topping up state

    Todo:
        Improve check that
    """

    # fmt:off
    #: WARNING: don't use this variable directly, but call the set method
    frq  : A[ SignalRW [ Frequency ] , PvSuffix( "selTrgSR"     ) , Format.UNCACHED_SIGNAL ]
    busy : A[ SignalR  [ StTrg     ] , PvSuffix( "seqTrgSRbusy" ) , Format.UNCACHED_SIGNAL ]

    # fmt:on

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return
    # Todo: add this check ... e.g. during stage?
        assert callable(self.parent.state.get_value), (
            "I need to check the state of the parent"
            " before I switch frequency,"
            " but I can not access the parent's state signal"
        )


    @AsyncStatus.wrap
    async def set(self, value: T_co) -> AsyncStatus:
        value = Frequency.from_value(value)
        chk = await self.parent.state.get_value()
        assert chk != ToppingUpState.ON, (
            f"{self.__class__.__name__}(name={self.name})"
            f" injection signaled on by signal {self.parent.state}"
            f" with value {chk}. Thus not switching frequency"
        )
        await self.frq.set(value)


class TopUpEngine(EpicsDevice, StandardReadable):
    """
    Todo:
        add extra structure to this device (proxy)
    """

    # fmt:off
    next_injection    : A[ SignalR[ float ], PvSuffix("estCntDwnS")      ,  Format.UNCACHED_SIGNAL ]
    injection_trigger : A[ SignalR[ StTrg ], PvSuffix("stTrg")           ,  Format.UNCACHED_SIGNAL ]

    state      : A[ SignalRW [ ToppingUpState ] , PvSuffix( "state"           ), Format.UNCACHED_SIGNAL ]
    current    : A[ SignalR  [ float          ] , PvSuffix( "rdCur"           ), Format.UNCACHED_SIGNAL ]
    sb_current : A[ SignalR  [ float          ] , PvSuffix( "rdCurCS"         ), Format.UNCACHED_SIGNAL ]
    n_bunches  : A[ SignalR  [ int            ] , PvSuffix( "setMaxNrBunches" ), Format.UNCACHED_SIGNAL ]
    # fmt:on

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.frq_switch = FrequencySwitch(*args, **kwargs)
        super().__init__(*args, **kwargs)


__all__ = ["TopUpEngine", "ToppingUpState", "Frequency"]
