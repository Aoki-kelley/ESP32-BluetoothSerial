import utime
import struct
from BluetoothSerial import SerialBTClass, BLEGlobalConst

serial_bt = SerialBTClass(name="BLE Slave", is_master=False)
serial_bt.begin()

try:
    while True:
        if serial_bt.get_state() != BLEGlobalConst.DEVICE_CONNECTED:
            print("MAC: ", serial_bt.ble_config_get("mac"))
            utime.sleep(1)
        else:
            if serial_bt.is_available():
                print(serial_bt.read())
            # serial_bt.send(struct.pack("BB", 14, 7))

        utime.sleep_ms(50)
except Exception as e:
    serial_bt.end()
    print(repr(e))
