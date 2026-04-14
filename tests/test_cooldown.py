import time

import pytest

from bact_bessyii_ophyd_async.utils.cooldown import Cooldown


def test_cooldown_uninitalised():
    delay = 0.5
    cool_down = Cooldown(name="testcdw", delay=delay)
    cool_down.reset()
    assert not cool_down.valid()

    assert cool_down.elapsed() == pytest.approx(0, abs=0.2)
    assert cool_down.remaining() == pytest.approx(delay, abs=0.2)


def test_cooldown_initalised():
    delay = 0.5
    cool_down = Cooldown(name="testcdw", delay=delay)
    cool_down.record()
    assert cool_down.valid()

    assert cool_down.elapsed() == pytest.approx(0, abs=0.2)
    assert cool_down.remaining() == pytest.approx(delay, abs=0.2)

    time.sleep(delay)

    assert cool_down.elapsed() == pytest.approx(delay, abs=0.2)
    assert cool_down.remaining() == pytest.approx(0.0, abs=0.2)
