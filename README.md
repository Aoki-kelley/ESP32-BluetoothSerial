# ESP32 Bluetooth Serial Library
  <p align="center">
    蓝牙（低功耗蓝牙）实现主从数据收发功能
  </p>

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL License][license-shield]][license-url]



## 目录

[TOC]

## 内容

### 如何开始

#### 配置要求

1. ESP32 moudle with bluetooth
2. Micropython v1.20 or later

#### 安装步骤

Clone the repo

```sh
git clone https://github.com/Aoki-kelley/ESP32-BluetoothSerial.git
```

#### 文件目录说明

```
ESP32-BluetoothSerial
│  LICENSE
│  README.md
│
└─BluetoothSerial
    │  BluetoothSerial.py  # the library
    │
    └─examples
            master_test.py
            slave_test.py
```



### 使用说明

需要一个ESP32模块做为主机端(master)，一个ESP32模块作为从机端(slave)，需要注意，开始数据传输之前要让主机端得到正确的从机端的MAC地址。ESP32模块默认使用随机地址，意味着每次重新运行模块或代码时都要重新确定地址

使用上类似Arduino的串口库，见 examples



目前存在一些问题：

- 从机发送，主机接收时，如果蓝牙连接断开将引发 OSError: [Errno 12] 错误



### 如何参与开源项目

贡献使开源社区成为一个学习、激励和创造的绝佳场所。你所作的任何贡献都是**非常感谢**的。


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。



### 作者

[Aoki-kelley (github.com)](https://github.com/Aoki-kelley)

 *您也可以在贡献者名单中参看所有参与该项目的开发者。*



### 版权说明

该项目遵守 GPL v3 授权许可，详情请参阅 [LICENSE.GPL-v3](https://github.com/Aoki-kelley/ESP32-BluetoothSerial/blob/master/LICENSE.GPL-v3)

该 README.md 模板遵守 MIT 协议，详情请参阅 [LICENSE.MIT](https://github.com/Aoki-kelley/ESP32-BluetoothSerial/blob/master/LICENSE.MIT)

### 鸣谢


- [MicroPython 文档— MicroPython中文 1.17 文档](http://micropython.com.cn/en/latet/index.html)
- [Heerkog/MicroPythonBLEHID: Human Interface Device (HID) over Bluetooth Low Energy (BLE) GATT library for MicroPython. (github.com)](https://github.com/Heerkog/MicroPythonBLEHID)
- [shaojintian/Best_README_template: 🌩最好的中文README模板⚡️Best README template (github.com)](https://github.com/shaojintian/Best_README_template)

<!-- links -->

[your-project-path]:https://github.com/Aoki-kelley/ESP32-BluetoothSerial/
[contributors-shield]: https://img.shields.io/github/contributors/Aoki-kelley/ESP32-BluetoothSerial.svg?style=flat-square
[contributors-url]: https://github.com/Aoki-kelley/ESP32-BluetoothSerial/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Aoki-kelley/ESP32-BluetoothSerial.svg?style=flat-square
[forks-url]: https://github.com/Aoki-kelley/ESP32-BluetoothSerial/network/members
[stars-shield]: https://img.shields.io/github/stars/Aoki-kelley/ESP32-BluetoothSerial.svg?style=flat-square
[stars-url]: https://github.com/Aoki-kelley/ESP32-BluetoothSerial/stargazers
[issues-shield]: https://img.shields.io/github/issues/Aoki-kelley/ESP32-BluetoothSerial.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/Aoki-kelley/ESP32-BluetoothSerial.svg
[license-shield]: https://img.shields.io/github/license/Aoki-kelley/ESP32-BluetoothSerial.svg?style=flat-square
[license-url]: https://github.com/Aoki-kelley/ESP32-BluetoothSerial/blob/master/LICENSE.GPL-v3
