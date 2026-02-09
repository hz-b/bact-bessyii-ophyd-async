import asyncio
import pprint

from bact_bessyii_ophyd_async.devices.raw.topup_engine import TopUpEngine


async def main():
    topup_engine = TopUpEngine(prefix="TOPUPCC:", name="topup")
    await topup_engine.connect()
    r = await topup_engine.read()
    pprint.pprint(r)


if __name__ == "__main__":
    asyncio.run(main())