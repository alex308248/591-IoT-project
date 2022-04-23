# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example shows connecting to the PN532 with I2C (requires clock
stretching support), SPI, or UART. SPI is best, it uses the most pins but
is the most reliable and universally supported.
After initialization, try waving various 13.56MHz RFID cards over it!
"""

import board
import busio
from digitalio import DigitalInOut
import ibm_cloud
import time

#
# NOTE: pick the import that matches the interface being used
#
from adafruit_pn532.i2c import PN532_I2C

# from adafruit_pn532.spi import PN532_SPI
# from adafruit_pn532.uart import PN532_UART

customersList = {"1_35_69_103"}
customerName = {"1_35_69_103": "Andy"}
productList = {"30_199_238_60":"butter milk", "22_199_238_60":"coffee", "50_159_238_60":"candy", "233_216_238_60":"cereals", "137_160_238_60":"ham"}



# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)
# Non-hardware
# pn532 = PN532_I2C(i2c, debug=False)

# With I2C, we recommend connecting RSTPD_N (reset) to a digital pin for manual
# harware reset
reset_pin = DigitalInOut(board.D6)
# On Raspberry Pi, you must also connect a pin to P32 "H_Request" for hardware
# wakeup! this means we don't need to do the I2C clock-stretch thing
req_pin = DigitalInOut(board.D12)
time.sleep(1)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
time.sleep(1)

# SPI connection:
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# cs_pin = DigitalInOut(board.D5)
# pn532 = PN532_SPI(spi, cs_pin, debug=False)

# UART connection
# uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=100)
# pn532 = PN532_UART(uart, debug=False)

ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

topic = "CustomerId"

client = ibm_cloud.connect_ibm()
#ibm_cloud.publish()

ibm_cloud.subscribe(client=client, topic="CustomerId")

print("Waiting for RFID/NFC card...")
foundCustomer = False
while True:
    if ibm_cloud.getResetFlag() == True:
        foundCustomer = False
        topic = "CustomerId"
        ibm_cloud.reset()
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print(".", end="")
    # Try again if no card is available.
    if uid is None:
        continue
    #print("Found card with UID:", [hex(i) for i in uid])
    print("Found card with UID:", [i for i in uid])
    #payload = [i for i in uid]
    payload = ""

    for i in uid:
        payload += (str(i) + "_")
    payload = payload.rstrip("_")

    if payload in customersList:
        if foundCustomer == False:
            customerId = payload
            #ibm_cloud.subscribe(client=client, topic=customerId + ":" + "reset")
            ibm_cloud.subscribe(client=client, topic=customerName[customerId] + ":" + "reset")
            #ibm_cloud.publish(client=client, topic=topic, payload=payload)
            ibm_cloud.publish(client=client, topic=topic, payload=customerName[payload])
            #topic = payload + ":" + "scanned_item"
            topic = customerName[customerId] + ":" + "scanned_item"
            foundCustomer = True
    elif payload in productList:
        if foundCustomer == True:
            ibm_cloud.publish(client=client, topic=topic, payload=productList[payload])
        else:
            print("Please scan your VIP card")
    #reset condition

    if payload == "{'action': 'reset'}":
        pass

    if payload == "41_217_238_60" and foundCustomer == True:
        #topic = customerId + ":" + "reset"
        topic = customerName[customerId] + ":" + "reset"
        ibm_cloud.publish(client=client, topic=topic, payload=payload)
        #ibm_cloud.publish(client=client, topic=topic, payload=payload)
    time.sleep(5)
    