"""Only working when connection to BESSY II

Twin does not yet provide a topup engine
"""
import pytest

from bact_bessyii_ophyd_async.devices.topup_engine.engine import RawTopUpEngine
from bact_bessyii_ophyd_async.devices.topup_engine.system import TopUpSystem


@pytest.mark.asyncio
async def test_raw_engine_startup():
    engine = RawTopUpEngine("TOPUPCC:", name="topup")
    await engine.connect()
    r = await engine.read()
    # 6 entries should be there
    assert len(r) == 6


@pytest.mark.asyncio
async def test_system_startup():
    topup = TopUpSystem(
        "TOPUPCC:", name="topup", target_current=25, acceptable_loss=0.1
    )
    await topup.connect()
    await topup.stage()
    r = await topup.read()
    # 6 entries should be there
    assert len(r) == 6
    r = await topup.describe()
    # 6 entries should be there
    assert len(r) == 6
    await topup.unstage()
    assert callable(topup.frequency.set)
    assert callable(topup.topup.set)
