# 591-IoT-project

## Introduction
The project work is targeted at giving students opportunity to obtain better knowledge and familiarity with sensing and IoT systems. We are going to build a self-service store by using Raspberry Pi, RFID sensor and RFID tags. 

There are several assumption in our project. First of all, we assume each customer have a FRID tag which represent their identity. Second, we assume each product will have a RFID tag on it self. Third, we assume all of the customer were already login in our webapp and ready for checkout.

## System Design

## Environment settings
Raspberry Pi Setup
```sh
pip install wiot-sdk
pip install board
pip install busio
pip install digitalio
pip install adafruit_pn532.i2c
```

Sever Setup
```sh
pip install -r requirement.txt
```

WebApp Setup
```sh
pip install wiotp-sdk
pip install flask
pip install flask-socketio
```

## How to run the code
Raspberry Pi
```sh
cd raspberrypi
python ShoppingCart.py
```

Sever
```sh
cd server
python main.py
```

WebApp
```sh
cd webapp
python main.py
```

