import logging
logging.basicConfig(level=logging.INFO)

import asyncio
import pprint

from bact_bessyii_ophyd_async.devices.pp.kicker_ps import KickerPS
from bact_bessyii_ophyd_async.devices.raw.delay import Delay
from bact_bessyii_ophyd_async.devices.pp.kicker import Kicker



async def read():
    kicker = Kicker(ps_prefix="PKDHKR:", delay_prefix="KDHKR:", name="vk")
    await kicker.connect()
    r = await kicker.read()
    pprint.pprint(r)
    return

    kicker = Kicker(ps_prefix="PKDVKR:", delay_prefix="KDVKR:", name="vk")
    await kicker.connect()
    r = await kicker.read()
    pprint.pprint(r)
    return

    kicker_ps = KickerPS(prefix="PKDVKR:", name="kicker_ps")
    delay = Delay(prefix="KDVKR:", name="delay")
    await kicker_ps.connect()
    await delay.connect()
    r = await kicker_ps.read()
    pprint.pprint(r)
    r2 = await delay.read()
    pprint.pprint(r2)


async def check(): 
    # delay = Delay(prefix="KDHKR:", name="delay")
    # await delay.connect()
    # await delay.stage()
    # await delay.unstage()

    kicker_ps = KickerPS(
        prefix="PKDHKR:", name="kicker_ps")
    await kicker_ps.connect()
    await kicker_ps.stage()
    await kicker_ps.set(1.0)
    print("Kicker reporting to be at correct value 1.0")

    
    await asyncio.sleep(2.0)
    await kicker_ps.set(0.0, timeout=30)
    print("Kicker reporting to be at correct value 0.0")
    
    await kicker_ps.stop()
    await kicker_ps.unstage()
    r = await kicker_ps.read()
    pprint.pprint(r)

    
async def main():
    await read()
    return
    await check()
    await asyncio.sleep(5.0)


if __name__ == "__main__":
    asyncio.run(main())
