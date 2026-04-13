"""

Todo:
   clear dependency interdependence of frequency and
   top up raw/pp
"""
import asyncio
import logging
from typing import Annotated as A, Union
from math import isclose
import time

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
        self._delay_after_last_swtich = 2.0
        return
    # Todo: add this check ... e.g. during stage?
        assert callable(self.parent.state.get_value), (
            "I need to check the state of the parent"
            " before I switch frequency,"
            " but I can not access the parent's state signal"
        )

    @AsyncStatus.wrap
    async def set(self, value: T_co) -> AsyncStatus:
        """
        Todo:
            add a timeout that the value changed
        """
        value = Frequency.from_value(value)
        for cnt in range(2):
            busy = await self.busy.get_value()
            if busy == StTrg.INACTIVE:
                self.log.warning("topup engine not busy")
                break
            else:
                self.log.warning("topup engine still busy")
        else:
            raise AssertionError(
                f"{self.__class__.__name__}(name={self.name})"
                f" injection signaled as busy by {self.busy}"
                f" with value {busy} (at round {cnt})."
                " Thus not switching frequency"
            )
        # Todo: only display this message if the busy message
        #       above was shown
        self.log.warning("topup engine not busy any more")

        for cnt in range(2):
            chk = await self.parent.state.get_value()
            if chk == ToppingUpState.OFF:
                break
        else:
            raise AssertionError(
                f"{self.__class__.__name__}(name={self.name})"
                f" injection signaled on by signal {self.parent.state}"
                f" with value {chk} (at round {cnt})."
                " Thus not switching frequency"
            )

        # only switch the frequency when the last off has been switched
        # at least delay_after_last_witch ago
        ts = self.parent.get_timestamp_from_last_off()
        delay = get_remaining_delay(ts, self._delay_after_last_swtich)
        if delay:
            self.log.warning(
                "%s name+%sfrequency switch delayed by %.2f seconds",
                self.__class__.__name__,
                self.name,
                delay
            )
            await asyncio.sleep(delay)

        await self.frq.set(value)



class TopUpEngine(EpicsDevice, StandardReadable):
    """
    Todo:
        add extra structure to this device (proxy)

        review structure of devices ... consider using dependency injection for frequency switch
    """

    # fmt:off
    next_injection    : A[ SignalR[ float ], PvSuffix("estCntDwnS")      ,  Format.UNCACHED_SIGNAL ]
    injection_trigger : A[ SignalR[ StTrg ], PvSuffix("stTrg")           ,  Format.UNCACHED_SIGNAL ]

    state      : A[ SignalRW [ ToppingUpState ] , PvSuffix( "state"           ), Format.UNCACHED_SIGNAL ]
    current    : A[ SignalR  [ float          ] , PvSuffix( "rdCur"           ), Format.UNCACHED_SIGNAL ]
    sb_current : A[ SignalR  [ float          ] , PvSuffix( "rdCurCS"         ), Format.UNCACHED_SIGNAL ]
    n_bunches  : A[ SignalRW [ int            ] , PvSuffix( "setMaxNrBunches" ), Format.UNCACHED_SIGNAL ]
    # fmt:on

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.frq_switch = FrequencySwitch(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self._timestamp_last_switch_off = None

    def get_timestamp_from_last_off(self) -> float:
        raise NotImplementedError("only availble if derived mode is used")


def get_remaining_delay(timestamp: float, necessary_delay: float) -> float:
    """check how long it was already delayed
    """
    now = time.time()
    dt = now - timestamp
    delay = necessary_delay - dt
    return max(delay, 0)


__all__ = ["TopUpEngine", "ToppingUpState", "Frequency"]
