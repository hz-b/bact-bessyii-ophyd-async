import asyncio
import pprint

from bact_bessyii_ophyd_async.devices.raw.delay import Delay
from bact_bessyii_ophyd_async.devices.raw.topup_engine import (
    TopUpEngine as TopUpEngineRaw,
    Frequency,
    ToppingUpState,
)
from bact_bessyii_ophyd_async.devices.pp.topup_engine import TopUpEngine
from bact_bessyii_ophyd_async.devices.pp.kicker_ps import KickerPS


async def read_raw():
    topup_engine = TopUpEngineRaw(prefix="TOPUPCC:", name="topup")
    await topup_engine.connect()
    r = await topup_engine.read()
    pprint.pprint(r)


async def read():
    kicker_ps = KickerPS(prefix="PKDVKR:", name="kicker_ps")
    await kicker_ps.connect()
    r = await kicker_ps.read()
    pprint.pprint(r)
    return

    delay = Delay(name="diag-dly", prefix="KIWR:")
    await delay.connect()
    r = await delay.read()
    pprint.pprint(r)

    topup_engine = TopUpEngine(
        prefix="TOPUPCC:",
        name="topup",
        target_current=20.0,
        acceptable_loss=2.0,
        requested_injection_frequency=Frequency.HALF_HZ,
    )
    await topup_engine.connect()
    r = await topup_engine.read()
    pprint.pprint(r)


async def check():

    topup_engine = TopUpEngine(
        prefix="TOPUPCC:",
        name="topup",
        target_current=10.0,
        acceptable_loss=2.0,
        requested_injection_frequency=Frequency.HALF_HZ,
    )
    await topup_engine.connect()
    await topup_engine.set(ToppingUpState.ON)


async def main():
    # await read_raw()
    # await read()
    await check()
    # await asyncio.sleep(5.0)


if __name__ == "__main__":
    asyncio.run(main())
