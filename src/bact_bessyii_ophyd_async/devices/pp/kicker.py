from ophyd_async.core import Device, StandardReadable

from .kicker_ps import KickerPS
from ..raw.delay import Delay


class Kicker(StandardReadable):
    def __init__(self, name:str, ps_prefix: str, delay_prefix: str):
        with self.add_children_as_readables():
            self.ps = KickerPS(prefix=ps_prefix)
            self.delay = Delay(prefix=delay_prefix)
        super().__init__(name=name)
