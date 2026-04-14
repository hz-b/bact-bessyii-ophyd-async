import asyncio
import pprint

from bact_bessyii_ophyd_async.devices.topup_engine.enums import ToppingUpState
from bact_bessyii_ophyd_async.devices.topup_engine.system import TopUpSystem


async def main():
    topup = TopUpSystem(
        "TOPUPCC:", name="topup", target_current=25, acceptable_loss=0.1
    )
    await topup.connect()
    print("topup describe")
    pprint.pprint(await topup.describe(), compact=True)
    print("topup read")
    pprint.pprint(await topup.read(), compact=True)

    # The topup system contains two entry points which are bluesky
    # compatible ... the frequency switch and the topup state
    # frequency switch to 0.5 Hz
    await topup.frequency.set(0.5)
    # switch topup state off
    await topup.topup.set(ToppingUpState.OFF)

if __name__ == "__main__":
    asyncio.run(main())