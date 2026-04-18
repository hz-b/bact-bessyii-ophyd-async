import logging
import asyncio
import aioca

logging.basicConfig(level=logging.INFO)

from bact_bessyii_ophyd_async.devices.topup_engine.enums import ToppingUpState
from bact_bessyii_ophyd_async.devices.topup_engine.system import TopUpSystem
from bact_bessyii_ophyd_async.devices.topup_engine.engine import RawTopUpEngine

from bluesky.run_engine import RunEngine
import bluesky.plans as bp


async def check_engine():
    engine = RawTopUpEngine(
        "TOPUPCC:", name="topup", 
    )
    await engine.connect()
    # await topup.connect()
    # return

    print("Test")
    RE= RunEngine()
    print("Exc")
    uid = RE(bp.count([engine], 2))
    print(f"fEnd {uid}\n\n")
    del RE
    del engine
    print("================================")


async def check_system():
    t_sys = TopUpSystem(
        "TOPUPCC:", name="topup", target_current=17.0, acceptable_loss=0.1,
    )
    await t_sys.connect()

    print("Test sys")
    RE= RunEngine()
    print("Exc sys")
    # uid = RE(bp.list_scan([t_sys], t_sys.frequency, [0.1, 0.5, 1.0, 0.1]))
    uid = RE(bp.list_scan([t_sys], t_sys.to_target, [ToppingUpState.OFF, ToppingUpState.ON, ToppingUpState.OFF]))
    print(f"fEnd  sys {uid}\n\n")
    print("================================")


    
if __name__ == "__main__":
    async def run():
        await check_system()        
        await aioca.purge_channel_caches() 
        await asyncio.sleep(2)
        
    asyncio.run(run())
