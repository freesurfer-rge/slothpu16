from typing import List

import bitarray.util
import pytest

from rwr_connector_board import RWRConnectorBoard


class TestRWR:
    @pytest.mark.parametrize("target_value", [65535])
    def test_smoke(self, target_value: int):
        rwrcb = RWRConnectorBoard()

        rwrcb.write_register(target_value)
        rwrcb.Clock(True)
        rwrcb.OE(False)
        rwrcb.send()
        rwrcb.Clock(False)
        rwrcb.send()

        rwrcb.recv()
        assert rwrcb.read_register() == target_value

        rwrcb.OE(True)
        rwrcb.send()
        rwrcb.recv()
        assert rwrcb.read_register() == 0

        rwrcb.OE(False)
        rwrcb.send()
        rwrcb.recv()
        assert rwrcb.read_register() == target_value

        # rwrcb.Reset(True)
        # rwrcb.send()
        # rwrcb.Reset(False)
        # rwrcb.send()
        # rwrcb.recv()
        # assert rwrcb.read_register() == 0
