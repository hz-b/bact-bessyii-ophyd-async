# test_frequency.py
import pytest

from bact_bessyii_ophyd_async.devices.topup_engine.enums import Frequency


# Replace 'your_module' with the real module path where Frequency is defined.


@pytest.mark.parametrize(
    "input_value, expected",
    [
        # That should not fail
        (Frequency.ONE_HZ, Frequency.ONE_HZ),
        (Frequency.HALF_HZ, Frequency.HALF_HZ),
        (Frequency.TENTH_HZ, Frequency.TENTH_HZ),

        # allowed float values
        (1.0, Frequency.ONE_HZ),
        (0.5, Frequency.HALF_HZ),
        (0.1, Frequency.TENTH_HZ),
        (1, Frequency.ONE_HZ),
        # Values that are close
        (1.0 + 1e-12, Frequency.ONE_HZ),
        (1.0 - 1e-12, Frequency.ONE_HZ),
        (0.5 + 1e-12, Frequency.HALF_HZ),
        (0.5 - 1e-12, Frequency.HALF_HZ),
        (0.1 + 1e-12, Frequency.TENTH_HZ),
        (0.1 - 1e-12, Frequency.TENTH_HZ),

    ],
)
def test_from_value_accepts_common_inputs(input_value, expected):
    """Common valid inputs map to the expected Frequency member."""
    result = Frequency.from_value(input_value)
    assert result is expected
    # also check string representation didn't change unexpectedly
    assert isinstance(result.value, str)
    pass

def test_from_value_handles_floating_point_imprecision():
    """
    """
    computed = 0.3 - 0.2
    # won't match 0.1 but only be close to it
    assert computed != 0.1
    result = Frequency.from_value(computed)
    assert result is Frequency.TENTH_HZ


@pytest.mark.parametrize(
    "bad_input",
    [
        "magnet",
        object(),
        None,
        0.3333333333,
        -1.0,
        # strings are let go by SubsetEnu
        # better to find out if that's really ok
        "1.0",
    ],
)
def test_from_value_invalid_raises_value_error(bad_input):
    """Invalid inputs should raise ValueError (not TypeError)."""
    with pytest.raises(ValueError):
        Frequency.from_value(bad_input)


def test_from_value_error_message_contains_value():
    """The ValueError message should include the problematic value for debugging."""
    bad = "not-a-frequency"
    with pytest.raises(ValueError) as exc:
        Frequency.from_value(bad)
    assert "not-a-frequency" in str(exc.value)
