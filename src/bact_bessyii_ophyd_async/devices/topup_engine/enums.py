from math import isclose
from typing import Union
from ophyd_async.core import SubsetEnum


class ToppingUpState(SubsetEnum):
    OFF = "TopUp Automatic OFF"
    ON = "TopUp Automatic ON"


class StTrg(SubsetEnum):
    INACTIVE = "inactive"
    ACTIVE = "active"


class Frequency(SubsetEnum):
    ONE_HZ = "1 Hz"
    HALF_HZ = "0.5 Hz"
    TENTH_HZ = "0.1 Hz"

    @classmethod
    def from_value(cls, value: Union["Frequency", float]):
        if isinstance(value, cls):
            return value

            # Reject strings explicitly
        if isinstance(value, str):
            raise ValueError(
                f"String inputs (like {value}) are not accepted by"
                " Frequency.from_value; pass a numeric value (int/float)"
                " or a Frequency member."
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{value!r} is not a valid Frequency or numeric value")

        mapping = {
            1.0: cls.ONE_HZ,
            0.5: cls.HALF_HZ,
            0.1: cls.TENTH_HZ,
        }

        for expected, freq in mapping.items():
            if isclose(numeric, expected, rel_tol=0.0, abs_tol=1e-9):
                return freq

        raise ValueError(f"{numeric} Hz is not supported (allowed: 1.0, 0.5, 0.1 Hz)")
