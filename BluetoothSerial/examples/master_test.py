import utime
import struct
from BluetoothSerial import SerialBTClass, BLEGlobalConst

serial_bt = SerialBTClass(name="BLE Master", is_master=True)
serial_bt.begin(b'\xfda*\x16ez')
print("MAC: ", serial_bt.ble_config_get("mac"))

try:
    while True:
        utime.sleep_ms(50)
        if serial_bt.get_state() == BLEGlobalConst.DEVICE_CONNECTED:
            # serial_bt.send(struct.pack("BB", 11, 3))
            if serial_bt.is_available():
                print(serial_bt.read())

except Exception as e:
    serial_bt.end()
    print(repr(e))
