# 591-IoT-project

## Introduction
The project work is targeted at giving students opportunity to obtain better knowledge and familiarity with sensing and IoT systems. We are going to build a self-service store by using Raspberry Pi, RFID sensor and RFID tags. 

There are several assumptions in our project. First of all, we assume each customer have a FRID tag which represent their identity. Second, we assume each product will have a RFID tag on itself. Third, we assume all of the customers were already login in our web app and ready for checkout.

## System Design
We will need a Raspberry Pi with RFID sensor, and two laptops to run the project.
1. Raspberry Pi: It will represent the checkout counter and send the user login message through `CustomerId` channel. After that, the scanned products name will be published to the {user} channel. When the raspberry pi receives the {customerName}reset message under the topic {customerName:reset}, it will change the variables back to default and wait for the next customer to scan his/her membership card.
2. Server: It will receive the user messages from Raspberry Pi and subscribe to the {user} channel. The server will use the data from the previous transaction to update the model. Then analyze the product and publish the suggestion to the webapp. Server will also update the database when it receives the reset message from webapp.
3. WebApp: Webapp will render a webpage for user and show the scanned product received from the raspberry pi, followed by the recommended product received from the server and calculate the total amount of the bill. When the customer clicks the `checkout` button on the webpage, it will publish a reset message to Server and Raspberry Pi.

![image](https://github.com/alex308248/591-IoT-project/blob/main/systemdiagram.png)

## Demo Steps
1. Run the three files on three different device and make sure each of them have connected to IBM Cloud.
2. Open the web page.
3. Scan a customer RFID tag, and it should shows the name of customer at the top of the web page. 
4. Scan a product tag, and it should shows the name of the product at the `scanned item` part, shows the suggsestion at the `suggestion product` part, and shows the cost at the `Total$`.
5. Excute the previous action with different product tag, it should update the suggestion product and cost.
6. Press the `Check out` bottom, which it will update the database and allow to scan a new customer Tag.
7. You should see the updated data in the `server/Groceries_dataset_new.csv` file.

## Environment settings
######Raspberry Pi Setup
```sh
$ pip install wiot-sdk
$ pip install board
$ pip install busio
$ pip install digitalio
$ pip install adafruit_pn532.i2c
```

######Server Setup
```sh
$ pip install -r requirement.txt
```

######WebApp Setup
```sh
$ pip3 install Flask
$ pip3 install flask-socketio
$ pip3 install python-dotenv
$ pip3 install wiotp-sdk
```
Create `.env` file in the webapp directory. Input following into `.env` file.
```
HOST=<IPv4 address>
```

## How to run the code

######Raspberry Pi
```sh
$ cd raspberrypi
$ python ShoppingCart.py
```

######Server
```sh
$ cd server
$ python main.py
```

######WebApp
```sh
$ cd webapp
$ python main.py
```

