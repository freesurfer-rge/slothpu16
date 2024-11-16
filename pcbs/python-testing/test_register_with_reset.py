from typing import List

import bitarray.util
import pytest

from rwr_connector_board import RWRConnectorBoard

pwr_2 = [2 ** x for x in range(16)]
pwr_2_off = [65535 - 2 ** x for x in range(16)]
pwr_2_off_2 = [65536 - 2 ** x for x in range(16)]
other_vals = [
    7,
    13,
    31,
    49,
    265,
    877,
    1399,
    1451,
    4013,
    5869,
    7919,
    8512,
    18181,
    19937,
    28657,
    39119,
    65001,
]

all_vals = pwr_2 + pwr_2_off + pwr_2_off_2 + other_vals


class TestRWR:
    @pytest.mark.parametrize("target_value", all_vals)
    def test_smoke(self, target_value: int):
        rwrcb = RWRConnectorBoard()

        # Check we can write a value
        rwrcb.write_register(target_value)
        rwrcb.Clock(True)
        rwrcb.Clock(False)
        assert rwrcb.read_register() == target_value

    @pytest.mark.parametrize("target_value", all_vals)
    def test_output_enable(self, target_value: int):
        rwrcb = RWRConnectorBoard()

        rwrcb.write_register(target_value)
        rwrcb.Clock(True)
        rwrcb.Clock(False)

        # Check output enable
        rwrcb.OE(True)
        assert rwrcb.read_register() == 0
        rwrcb.OE(False)
        assert rwrcb.read_register() == target_value

    @pytest.mark.parametrize("target_value", all_vals)
    def test_reset(self, target_value: int):
        rwrcb = RWRConnectorBoard()

        rwrcb.write_register(target_value)
        rwrcb.Clock(True)
        rwrcb.Clock(False)
        assert rwrcb.read_register() == target_value

        # Check Reset line
        rwrcb.Reset()
        assert rwrcb.read_register() == 0
