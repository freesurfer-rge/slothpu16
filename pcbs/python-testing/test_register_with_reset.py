from typing import List

import bitarray.util
import pytest

from rwr_connector_board import RWRConnectorBoard

pwr_2 = [2**x for x in range(16)]
pwr_2_off = [65535 - 2**x for x in range(16)]
pwr_2_off_2 = [65536 - 2**x for x in range(16)]

all_vals = pwr_2 + pwr_2_off + pwr_2_off_2

class TestRWR:
    @pytest.mark.parametrize("target_value", all_vals)
    def test_smoke(self, target_value: int):
        rwrcb = RWRConnectorBoard()
        rwrcb.OE(False)
        rwrcb.Reset(True)

        # Check we can write a value
        rwrcb.write_register(target_value)
        rwrcb.Clock(False)
        rwrcb.Clock(True)
        rwrcb.Clock(False)
        assert rwrcb.read_register() == target_value

        # Check output enable
        rwrcb.OE(True)
        assert rwrcb.read_register() == 0
        rwrcb.OE(False)
        assert rwrcb.read_register() == target_value

        # Check Reset line
        rwrcb.Reset(False)
        rwrcb.Reset(True)
        assert rwrcb.read_register() == 0
