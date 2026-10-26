"""Prueba de control de bateria SAJ H1 por Modbus TCP.

Uso:
  python saj_test.py <ip> snapshot            # solo lectura, guarda backup
  python saj_test.py <ip> watch [segundos]    # monitoriza potencia/SOC/modos
  python saj_test.py <ip> selfuse             # AppMode=0
  python saj_test.py <ip> standby             # Passive=0, AppMode=3
  python saj_test.py <ip> charge <W>          # Passive charge power=W, Passive=2, AppMode=3
  python saj_test.py <ip> restore             # reescribe los valores del backup

Antes de usarlo, desactiva la conexion Modbus de Home Assistant: el modulo
AIO3 no admite bien dos clientes a la vez.
"""

import json
import sys
import time
from pathlib import Path

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

DEVICE_ID = 1
BACKUP_FILE = Path(__file__).with_name("saj_backup.json")

REG_APP_MODE = 0x3247
REG_PASSIVE_MODE = 0x3636
REG_PASSIVE_CHARGE_POWER = 0x3637
REG_PASSIVE_DISCHARGE_POWER = 0x3638

APP_MODES = {0: "SELF_USE", 1: "TIME_OF_USE", 2: "BACKUP", 3: "PASSIVE"}
# Mapeo segun el PDF de SAJ. En este H1-5K-S2 el valor 2 descargo la bateria
# exportando ~500 W a red (prueba 26/10/2026), al contrario que ha-saj-h1-mqtt.
PASSIVE_MODES = {0: "STANDBY", 1: "CHARGE", 2: "DISCHARGE"}
PASSIVE_CHARGE = 1

# Registros que se guardan en el backup y se pueden restaurar
BACKUP_REGS = [REG_APP_MODE, REG_PASSIVE_MODE, REG_PASSIVE_CHARGE_POWER, REG_PASSIVE_DISCHARGE_POWER]


def s16(v):
    return v - 0x10000 if v >= 0x8000 else v


def read(client, addr, count=1, retries=3):
    # El AIO3 devuelve a veces tramas corruptas: reintentar reconectando
    for attempt in range(retries):
        try:
            rr = client.read_holding_registers(address=addr, count=count, device_id=DEVICE_ID)
            if not rr.isError() and len(rr.registers) == count:
                time.sleep(0.3)
                return rr.registers
            # respuesta de error o desfasada (otro numero de registros)
            err = rr
        except ModbusException as ex:
            err = ex
        client.close()
        time.sleep(1 + attempt)
        client.connect()
    raise RuntimeError(f"Error leyendo 0x{addr:04X}: {err}")


def write(client, addr, value):
    print(f"  escribiendo 0x{addr:04X} ({addr}) = {value}")
    rr = client.write_register(address=addr, value=value, device_id=DEVICE_ID)
    if rr.isError():
        raise RuntimeError(f"Error escribiendo 0x{addr:04X}: {rr}")
    time.sleep(1.5)
    back = read(client, addr)[0]
    print(f"  releido 0x{addr:04X} = {back} {'OK' if back == value else 'NO COINCIDE'}")


def status(client):
    app = read(client, REG_APP_MODE)[0]
    passive, chg, dis = read(client, REG_PASSIVE_MODE, 3)
    soc = read(client, 0x406F)[0] / 100
    bat_dir = s16(read(client, 0x4096)[0])
    block = read(client, 0x40A0, 8)  # 0x40A0..0x40A7 en una sola peticion
    load_w, pv_w, bat_w, grid_w = (s16(block[i]) for i in (0, 5, 6, 7))
    # candidatos a potencia de red (0x40A7 devuelve 0 de noche)
    grid_4035 = s16(read(client, 0x4035)[0])
    grid_40ad = s16(read(client, 0x40AD)[0])
    return {
        "app_mode": f"{app} {APP_MODES.get(app, '?')}",
        "passive_mode": f"{passive} {PASSIVE_MODES.get(passive, '?')}",
        "passive_charge_W": chg,
        "passive_discharge_W": dis,
        "soc_%": soc,
        "bateria_W": bat_w,
        "bateria_dir": bat_dir,
        "red_W": grid_w,
        "red_4035": grid_4035,
        "red_40AD": grid_40ad,
        "pv_W": pv_w,
        "consumo_W": load_w,
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    ip, cmd = sys.argv[1], sys.argv[2]
    client = ModbusTcpClient(ip, port=502, timeout=5)
    if not client.connect():
        sys.exit(f"No conecta a {ip}:502")
    try:
        if cmd == "snapshot":
            values = {f"0x{a:04X}": read(client, a)[0] for a in BACKUP_REGS}
            if BACKUP_FILE.exists():
                print(f"Backup ya existe, no se sobrescribe: {BACKUP_FILE}")
            else:
                BACKUP_FILE.write_text(json.dumps(values, indent=2))
                print(f"Backup guardado en {BACKUP_FILE}")
            print(json.dumps(values, indent=2))
            print(json.dumps(status(client), indent=2))
        elif cmd == "watch":
            secs = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            end = time.time() + secs
            while time.time() < end:
                try:
                    print(time.strftime("%H:%M:%S"), status(client), flush=True)
                except RuntimeError as ex:
                    print(time.strftime("%H:%M:%S"), "lectura fallida:", ex, flush=True)
                time.sleep(5)
        elif cmd == "selfuse":
            write(client, REG_APP_MODE, 0)
        elif cmd == "standby":
            write(client, REG_PASSIVE_MODE, 0)
            write(client, REG_APP_MODE, 3)
        elif cmd == "charge":
            watts = int(sys.argv[3])
            if not 100 <= watts <= 2500:
                sys.exit("Potencia fuera de rango de prueba (100-2500 W)")
            write(client, REG_PASSIVE_CHARGE_POWER, watts)
            write(client, REG_PASSIVE_MODE, PASSIVE_CHARGE)
            write(client, REG_APP_MODE, 3)
        elif cmd == "restore":
            values = json.loads(BACKUP_FILE.read_text())
            # AppMode al final, para que el modo pasivo quede configurado antes
            for key in sorted(values, key=lambda k: int(k, 16) == REG_APP_MODE):
                write(client, int(key, 16), values[key])
        else:
            sys.exit(f"Comando desconocido: {cmd}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
