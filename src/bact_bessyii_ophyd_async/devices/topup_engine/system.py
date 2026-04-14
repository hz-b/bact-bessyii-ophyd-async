from bluesky.protocols import Stoppable, Stageable
from ophyd_async.core import AsyncMovable, AsyncStatus, StandardReadable
from ophyd_async.epics.core import EpicsDevice


from ...utils.cooldown import Cooldown
from .controller import TopUpController
from .engine import RawTopUpEngine
from .enums import ToppingUpState, Frequency
from .policy import TopUpPolicy


class ToppingUpToTargetCurrent(AsyncMovable):
    def __init__(self, controller: TopUpController):
        self.controller = controller

    @AsyncStatus.wrap
    async def set(self, value: ToppingUpState):
        value = ToppingUpState(value)

        if value == ToppingUpState.ON:
            await self.controller.start()
            await self.controller.wait_for_toppingup_to_finish()
        else:
            await self.controller.stop()


class TopUpStateProxy(AsyncMovable):
    def __init__(self, controller: TopUpController):
        self.controller = controller

    @AsyncStatus.wrap
    async def set(self, value: ToppingUpState):
        value = ToppingUpState(value)

        if value == ToppingUpState.ON:
            await self.controller.start()
        else:
            await self.controller.stop()


class FrequencyProxy(AsyncMovable):
    def __init__(self, controller: TopUpController):
        self.controller = controller

    @AsyncStatus.wrap
    async def set(self, value: Frequency):
        await self.controller.set_frequency(value)


class TopUpSystem(EpicsDevice, StandardReadable, Stoppable, Stageable):
    """
    High-level system device combining:
    - EPICS signals (engine)
    - control logic (controller)
    - AsyncMovable interfaces (proxies)
    """

    def __init__(
        self,
        *args,
        target_current: float,
        acceptable_loss: float,
        cooldown_time: float = 2.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # -------------------------
        # Device layer
        with self.add_children_as_readables():
            self.engine = RawTopUpEngine(*args, **kwargs)
        # -------------------------
        # Logic layer
        self.cooldown = Cooldown(name="topup off", delay=cooldown_time)
        self.controller = TopUpController(
            engine=self.engine,
            policy=TopUpPolicy(
                target_current=target_current,
                acceptable_loss=acceptable_loss,
            ),
            cooldown=self.cooldown,
            log=self.log,
        )
        # -------------------------
        # Control surface
        self.state = TopUpStateProxy(self.controller)
        self.frequency = FrequencyProxy(self.controller)
        self.to_target = ToppingUpToTargetCurrent(self.controller)
        # -------------------------

    async def stage(self) -> None:
        await self.engine.stage()

    async def unstage(self) -> None:
        await self.engine.unstage()

    async def read(self):
        return await self.engine.read()

    async def stop(self, success=True):
        st = self.engine.stop()
        self.cooldown.reset()
        await st


__all__ = ["TopUpSystem"]
