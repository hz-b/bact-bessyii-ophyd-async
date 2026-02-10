from ophyd_async.core import AsyncStageable, WatchableAsyncStatus, AsyncStatus
from bluesky.protocols import Stoppable

from bact_bessyii_mls_ophyd.devices.utils.pv_positioner_like_utils import _SettableControllingDifference

from ..raw.kicker_ps import KickerPS as RawKickerPS, PoweredState, HighVoltageState


class KickerPS(RawKickerPS, _SettableControllingDifference, AsyncStageable, Stoppable):
    def __init__(self, *args, deactivate_on_stop: bool = True, **kwargs):
        self.deactivate_on_stop = bool(deactivate_on_stop)
        eps_abs = kwargs.pop("eps_abs", 4e-2)
        eps_rel = kwargs.pop("eps_rel", 2e-2)
        super().__init__(*args, **kwargs)
        kwargs.pop("prefix", None)
        _SettableControllingDifference.__init__(self, *args, eps_abs=eps_abs, eps_rel=eps_rel, **kwargs)

    @AsyncStatus.wrap        
    async def stage(self):
        pw = await self.powered.get_value()
        hv = await self.hv_on.get_value()
        self.log.warning(f"{self.__class__.__name__} {pw=} {hv=}")
        assert pw == PoweredState.ON, f"{self.__class__.__name__} is not on"
        assert hv == HighVoltageState.ON, f"{self.__class__.__name__} high voltage is not on"
        return await super().stage()

    @AsyncStatus.wrap        
    async def unstage(self):
        return await super().unstage()

    @AsyncStatus.wrap        
    async def stop(self, success=False):
        self.log.warning(f'Stopping kicker ps "{self.name}"')
        if self.deactivate_on_stop:
            self.log.warning(f'Setting back kicker ps "{self.name}"')
            await self.setpoint.set(0)

    @AsyncStatus.wrap
    async def set(self, new_position: float, timeout: float=30.0):
        """
        Todo:
           timeout should be computed from last value and target

        Ramp down is basically a discharge ... so there the time out
        must be much longer
        """
        return await _SettableControllingDifference.set(self, new_position, timeout=timeout)
