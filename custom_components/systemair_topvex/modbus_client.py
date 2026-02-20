"""Low-level Modbus TCP client for Systemair Topvex."""
from __future__ import annotations

import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import MAX_REGISTERS_PER_REQUEST

_LOGGER = logging.getLogger(__name__)


def signed16(val: int) -> int:
    """Convert unsigned 16-bit to signed."""
    return val - 65536 if val > 32767 else val


class TopvexModbusClient:
    """Async Modbus TCP client for Topvex Access controller."""

    def __init__(self, host: str, port: int, unit_id: int) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self._client: AsyncModbusTcpClient | None = None

    async def connect(self) -> bool:
        """Connect to the Modbus device."""
        self._client = AsyncModbusTcpClient(
            host=self.host,
            port=self.port,
            timeout=5,
        )
        return await self._client.connect()

    async def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self._client:
            self._client.close()
            self._client = None

    @property
    def connected(self) -> bool:
        """Return True if connected."""
        return self._client is not None and self._client.connected

    async def read_input_registers(
        self, address: int, count: int
    ) -> list[int] | None:
        """Read input registers (FC 0x04). Returns raw unsigned values."""
        if not self.connected:
            return None
        if count > MAX_REGISTERS_PER_REQUEST:
            raise ValueError(
                f"Cannot read {count} registers (max {MAX_REGISTERS_PER_REQUEST})"
            )
        try:
            result = await self._client.read_input_registers(
                address=address, count=count, slave=self.unit_id
            )
            if result.isError():
                _LOGGER.debug(
                    "Modbus error reading IR %d-%d: %s",
                    address, address + count - 1, result,
                )
                return None
            return list(result.registers)
        except ModbusException as err:
            _LOGGER.debug("Modbus exception reading IR %d: %s", address, err)
            return None

    async def read_holding_registers(
        self, address: int, count: int
    ) -> list[int] | None:
        """Read holding registers (FC 0x03). Returns raw unsigned values."""
        if not self.connected:
            return None
        if count > MAX_REGISTERS_PER_REQUEST:
            raise ValueError(
                f"Cannot read {count} registers (max {MAX_REGISTERS_PER_REQUEST})"
            )
        try:
            result = await self._client.read_holding_registers(
                address=address, count=count, slave=self.unit_id
            )
            if result.isError():
                _LOGGER.debug(
                    "Modbus error reading HR %d-%d: %s",
                    address, address + count - 1, result,
                )
                return None
            return list(result.registers)
        except ModbusException as err:
            _LOGGER.debug("Modbus exception reading HR %d: %s", address, err)
            return None

    async def write_register(self, address: int, value: int) -> bool:
        """Write a single holding register (FC 0x06)."""
        if not self.connected:
            return False
        if value < 0:
            value += 65536
        try:
            result = await self._client.write_register(
                address=address, value=value, slave=self.unit_id
            )
            if result.isError():
                _LOGGER.error(
                    "Modbus error writing HR %d = %d: %s", address, value, result
                )
                return False
            return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing HR %d: %s", address, err)
            return False

    async def write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil (FC 0x05)."""
        if not self.connected:
            return False
        try:
            result = await self._client.write_coil(
                address=address, value=value, slave=self.unit_id
            )
            if result.isError():
                _LOGGER.error(
                    "Modbus error writing coil %d: %s", address, result
                )
                return False
            return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing coil %d: %s", address, err)
            return False

    async def read_input_register_single(self, address: int) -> int | None:
        """Read a single input register, return signed value / 10."""
        regs = await self.read_input_registers(address, 1)
        if regs is None:
            return None
        return signed16(regs[0]) / 10
