import bluetooth
import struct
from micropython import const

BUFFER_MODE_LOOP = const(0x01)  # 缓冲区循环
BUFFER_MODE_BLOCK = const(0x02)  # 缓冲区阻塞


class BLEGlobalConst:
    """BLE 常量"""

    # for BLE service
    BLE_READ_FLAG = bluetooth.FLAG_READ
    BLE_WRITE_FLAG = bluetooth.FLAG_WRITE
    BLE_NOTIFY_FLAG = bluetooth.FLAG_NOTIFY

    # for ATT
    ATT_READ_FLAG = const(0x01)
    ATT_WRITE_FLAG = const(0x02)

    # IRQ Events
    IRQ_CENTRAL_CONNECT = const(1)
    IRQ_CENTRAL_DISCONNECT = const(2)
    IRQ_GATTS_WRITE = const(3)
    IRQ_GATTS_READ_REQUEST = const(4)
    IRQ_SCAN_RESULT = const(5)
    IRQ_SCAN_DONE = const(6)
    IRQ_PERIPHERAL_CONNECT = const(7)
    IRQ_PERIPHERAL_DISCONNECT = const(8)
    IRQ_GATTC_SERVICE_RESULT = const(9)
    IRQ_GATTC_SERVICE_DONE = const(10)
    IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
    IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
    IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
    IRQ_GATTC_DESCRIPTOR_DONE = const(14)
    IRQ_GATTC_READ_RESULT = const(15)
    IRQ_GATTC_READ_DONE = const(16)
    IRQ_GATTC_WRITE_DONE = const(17)
    IRQ_GATTC_NOTIFY = const(18)
    IRQ_GATTC_INDICATE = const(19)
    IRQ_GATTS_INDICATE_DONE = const(20)
    IRQ_MTU_EXCHANGED = const(21)
    IRQ_L2CAP_ACCEPT = const(22)
    IRQ_L2CAP_CONNECT = const(23)
    IRQ_L2CAP_DISCONNECT = const(24)
    IRQ_L2CAP_RECV = const(25)
    IRQ_L2CAP_SEND_READY = const(26)
    IRQ_CONNECTION_UPDATE = const(27)
    IRQ_ENCRYPTION_UPDATE = const(28)
    IRQ_GET_SECRET = const(29)
    IRQ_SET_SECRET = const(30)
    IRQ_PASSKEY_ACTION = const(31)

    # Response for Event IRQ_GATTS_READ_REQUEST
    GATTS_NO_ERROR = const(0)
    GATTS_ERROR_READ_NOT_PERMITTED = const(2)
    GATTS_ERROR_WRITE_NOT_PERMITTED = const(3)
    GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(5)
    GATTS_ERROR_INSUFFICIENT_AUTHORIZATION = const(8)
    GATTS_ERROR_INSUFFICIENT_ENCRYPTION = const(15)

    # Action for Event IRQ_PASSKEY_ACTION
    PASSKEY_ACTION_NONE = const(0)
    PASSKEY_ACTION_INPUT = const(2)
    PASSKEY_ACTION_DISPLAY = const(3)
    PASSKEY_ACTION_NUMERIC_COMPARISON = const(4)

    # the State of Device
    DEVICE_STOPPED = const(0)
    DEVICE_IDLE = const(1)
    DEVICE_ADVERTISING = const(2)
    DEVICE_CONNECTED = const(3)

    # for Advertiser
    ADV_TYPE_FLAGS = const(0x01)
    ADV_TYPE_NAME = const(0x09)
    ADV_TYPE_UUID16_COMPLETE = const(0x3)
    ADV_TYPE_UUID32_COMPLETE = const(0x5)
    ADV_TYPE_UUID128_COMPLETE = const(0x7)
    ADV_TYPE_UUID16_MORE = const(0x2)
    ADV_TYPE_UUID32_MORE = const(0x4)
    ADV_TYPE_UUID128_MORE = const(0x6)
    ADV_TYPE_APPEARANCE = const(0x19)


# 将需要广播的数据打包
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=None):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        BLEGlobalConst.ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(BLEGlobalConst.ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(BLEGlobalConst.ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(BLEGlobalConst.ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(BLEGlobalConst.ADV_TYPE_UUID128_COMPLETE, b)

    if appearance:
        _append(BLEGlobalConst.ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload


class SerialBTClass:
    """简单的蓝牙主从收发类"""

    def __init__(self, name, is_master=True):
        self.name = name
        self.is_master = is_master

        self.__ble = bluetooth.BLE()
        self.__ble.active(True)
        self.__ble.config(gap_name=self.name)
        self.__ble.config(mtu=23)
        self.__ble.config(addr_mode=0x01)

        service_uuid = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        reader_uuid = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        sender_uuid = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        self.__services = (
            (
                bluetooth.UUID(service_uuid),
                (
                    (bluetooth.UUID(sender_uuid), BLEGlobalConst.BLE_NOTIFY_FLAG),
                    (bluetooth.UUID(reader_uuid), BLEGlobalConst.BLE_WRITE_FLAG),
                )
            ),
        )
        self.__handles = self.__ble.gatts_register_services(self.__services)
        ((self.__tx_handle, self.__rx_handle,),) = self.__handles

        self.__conn_handle = None

        self.__state = BLEGlobalConst.DEVICE_IDLE
        self.__buffer_size = 256
        self.__buffer_mode = BUFFER_MODE_LOOP
        self.__write_buffer = b""
        self.__read_buffer = [0 for _ in range(self.__buffer_size)]
        self.__read_buffer_point = -1

    def ble_config_get(self, param):
        return self.__ble.config(str(param))

    def set_buffer_mode(self, _value):
        if _value == BUFFER_MODE_LOOP:
            self.__buffer_mode = BUFFER_MODE_LOOP
        elif _value == BUFFER_MODE_BLOCK:
            self.__buffer_mode = BUFFER_MODE_BLOCK

    def begin(self, slave_addr=None):
        self.__ble.irq(self.__ble_irq)
        self.__set_state(BLEGlobalConst.DEVICE_IDLE)
        if self.is_master:
            if slave_addr:
                self.__ble.gap_connect(0x01, slave_addr)
                while self.__state != BLEGlobalConst.DEVICE_CONNECTED:
                    pass
            else:
                raise Exception("未指定从机地址")
        else:
            self.__start_advertising()

    def end(self):
        if self.is_master:
            self.__ble.gap_disconnect(self.__conn_handle)
        else:
            self.__stop_advertising()

        self.__set_state(BLEGlobalConst.DEVICE_IDLE)

    def is_available(self):
        if self.__read_buffer_point >= 0:
            return True
        else:
            return False

    def send(self, _data):
        if self.__conn_handle is None:
            return

        self.__write_buffer = _data
        if not self.is_master:
            self.__ble.gatts_notify(self.__conn_handle, self.__tx_handle, _data)
        else:
            self.__ble.gattc_write(self.__conn_handle, self.__rx_handle, _data)

    def read(self):
        ret = self.peek()
        if self.__read_buffer_point >= 0:
            self.__read_buffer_point -= 1
        return ret

    def peek(self):
        if self.__read_buffer_point < 0:
            return
        else:
            return self.__read_buffer[self.__read_buffer_point]

    def get_state(self):
        return self.__state

    def __start_advertising(self):
        if self.__state is not BLEGlobalConst.DEVICE_STOPPED and \
                self.__state is not BLEGlobalConst.DEVICE_ADVERTISING:
            adv_data = advertising_payload(name=self.name)
            self.__ble.gap_advertise(100000, adv_data)
            # print("Started advertising")
            self.__set_state(BLEGlobalConst.DEVICE_ADVERTISING)

    def __stop_advertising(self):
        if self.__state is not BLEGlobalConst.DEVICE_STOPPED:
            self.__ble.gap_advertise(0, b"")
            # print("Stopped advertising")
            if self.__state is not BLEGlobalConst.DEVICE_CONNECTED:
                self.__set_state(BLEGlobalConst.DEVICE_IDLE)

    def __set_state(self, state):
        # print("Device state changed: ", self.__state, "->", state)
        self.__state = state

    def __buffer_append(self, _v):
        if self.__buffer_mode == BUFFER_MODE_LOOP:
            if self.__read_buffer_point < self.__buffer_size - 1:
                self.__read_buffer_point += 1
            else:
                self.__read_buffer_point = 0
            self.__read_buffer[self.__read_buffer_point] = _v
        elif self.__buffer_mode == BUFFER_MODE_BLOCK:
            if self.__read_buffer_point < self.__buffer_size - 1:
                self.__read_buffer_point += 1
                self.__read_buffer[self.__read_buffer_point] = _v

    def __ble_irq(self, event, data):
        if event == BLEGlobalConst.IRQ_CENTRAL_CONNECT:  # 中心设备建立连接
            self.__conn_handle, addr_type, addr = data
            # print("Central connected: ", self.__conn_handle)
            self.__stop_advertising()
            self.__set_state(BLEGlobalConst.DEVICE_CONNECTED)
        elif event == BLEGlobalConst.IRQ_CENTRAL_DISCONNECT:  # 中心设备断开连接
            self.__conn_handle = None
            conn_handle, _, _ = data
            # print("Central disconnected: ", conn_handle)
            self.__start_advertising()
            self.__set_state(BLEGlobalConst.DEVICE_IDLE)
        elif event == BLEGlobalConst.IRQ_GATTS_WRITE:  # 写入请求
            buffer = self.__ble.gatts_read(self.__rx_handle).decode('UTF-8').strip()
            # print("GATTs Write: ", data, buffer)
            self.__buffer_append(buffer)
        elif event == BLEGlobalConst.IRQ_PERIPHERAL_CONNECT:  # 外围设备建立连接
            self.__conn_handle, addr_type, addr = data
            # print("Peripheral connected: ", self.__conn_handle)
            self.__set_state(BLEGlobalConst.DEVICE_CONNECTED)
            self.__ble.gattc_exchange_mtu(self.__conn_handle)
        elif event == BLEGlobalConst.IRQ_PERIPHERAL_DISCONNECT:  # 外围设备断开连接
            self.__conn_handle = None
            conn_handle, _, _ = data
            # print("Peripheral disconnected: ", conn_handle)
            self.__conn_handle = None
            self.__set_state(BLEGlobalConst.DEVICE_IDLE)
        elif event == BLEGlobalConst.IRQ_GATTC_NOTIFY:  # 收到广播数据
            _, _, notify_data = data
            # print(bytes.fromhex(notify_data.hex()))
            self.__buffer_append(bytes.fromhex(notify_data.hex()))
        elif event == BLEGlobalConst.IRQ_MTU_EXCHANGED:  # MTU 更改
            conn_handle, mtu = data
            self.__ble.config(mtu=mtu)
            # print("MTU changed: ", mtu)
        elif event == BLEGlobalConst.IRQ_CONNECTION_UPDATE:  # 连接属性更新
            self.__conn_handle, _, _, _, _ = data
            # print("Connection update")
        elif event == BLEGlobalConst.IRQ_ENCRYPTION_UPDATE:
            # print("Encryption update: ", data)
            pass
        else:
            # print("Unhandled IRQ event: ", event, data)
            pass


if __name__ == "__main__":
    pass
