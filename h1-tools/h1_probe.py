"""Sondeo de solo lectura: que bloques de la integracion H2 responde un SAJ H1.

Uso:
  python h1_probe.py <ip> [salida.json]

Lee cada bloque que consulta la integracion saj_h2_modbus (y los bloques
propios del H1) y guarda si responde, el codigo de excepcion y los valores.
No escribe ningun registro. Requiere que ningun otro cliente Modbus (p. ej.
Home Assistant) este conectado al modulo AIO3.
"""

import json
import sys
import time

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

DEVICE_ID = 1

# (nombre, direccion, cantidad)
BLOCKS = [
    # Bloques leidos por saj_h2_modbus (modbus_readers.py)
    ("h2_inverter_info", 0x8F00, 29),
    ("h2_realtime", 16388, 19),
    ("h2_additional_4_grid_phase", 16433, 21),
    ("h2_inverter_phase", 16454, 15),
    ("h2_offgrid_output", 16469, 18),
    ("h2_side_net", 16525, 8),
    ("h2_additional_1_part_1", 0x4067, 22),
    ("h2_additional_1_part_2", 16533, 25),
    ("h2_additional_2_part_1", 16575, 32),
    ("h2_additional_2_part_2", 16607, 32),
    ("h2_additional_3", 16695, 30),
    ("h2_additional_3_2", 16725, 34),
    ("h2_inverter_settings", 0x4023, 14),
    ("h2_battery_data", 0xA000, 56),
    ("h2_meter_a", 0xA03D, 18),
    ("h2_charge_schedule", 0x3604, 23),
    ("h2_discharge_schedule", 0x361B, 21),
    ("h2_passive_anti_reflux", 0x3636, 43),
    ("h2_app_mode_0x3647", 0x3647, 1),
    # Bloques H1 (protocolo SAJ 2020 / ha-saj-h1-mqtt)
    ("h1_inverter_info", 0x8F00, 30),
    ("h1_bms_info", 0x8E00, 0x50),
    ("h1_realtime_0x4000", 0x4000, 0x76),
    ("h1_summaries", 0x4076, 0x49),
    ("h1_energies", 0x40BF, 0x41),
    ("h1_battery_ctrl", 0xA000, 0x24),
    ("h1_config_0x3247", 0x3247, 0x2E),
    ("h1_schedule_0x3604", 0x3604, 0x35),
    ("h1_passive_0x3636", 0x3636, 3),
    ("h1_app_mode_0x3247", 0x3247, 1),
]


def read_block(client, addr, count, retries=3):
    """Lee en trozos de hasta 100 registros; devuelve (ok, valores|error)."""
    values = []
    pos, left = addr, count
    while left > 0:
        n = min(left, 100)
        err = None
        for attempt in range(retries):
            try:
                rr = client.read_holding_registers(address=pos, count=n, device_id=DEVICE_ID)
                if rr.isError():
                    # una excepcion Modbus es una respuesta valida: no reintentar
                    return False, f"exc {rr.exception_code}"
                if len(rr.registers) == n:
                    values.extend(rr.registers)
                    break
                err = f"longitud {len(rr.registers)} != {n} (respuesta desfasada)"
            except ModbusException as ex:
                err = str(ex)
            client.close()
            time.sleep(1 + attempt)
            client.connect()
        else:
            return False, err
        pos += n
        left -= n
        time.sleep(0.5)
    return True, values


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ip = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "h1_probe_result.json"
    client = ModbusTcpClient(ip, port=502, timeout=5)
    if not client.connect():
        sys.exit(f"No conecta a {ip}:502")
    result = {}
    try:
        for name, addr, count in BLOCKS:
            ok, data = read_block(client, addr, count)
            result[name] = {"address": f"0x{addr:04X}", "count": count, "ok": ok, "data": data}
            summary = f"{len(data)} regs, primeros {data[:6]}" if ok else data
            print(f"{'OK ' if ok else 'ERR'} {name:30s} 0x{addr:04X} x{count:<3d} {summary}", flush=True)
            time.sleep(1)
    finally:
        client.close()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print(f"Resultado guardado en {out}")


if __name__ == "__main__":
    main()
