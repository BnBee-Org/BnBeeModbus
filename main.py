# ---------------------------
#       Script 2.0
#       Ostap Kuch
#       25.09.2022
# ---------------------------

import time
import serial
import requests
from pytz import timezone
from datetime import datetime
import re

CREATE_NEW_DB = False
SERIAL_TIMEOUT = 1.5
BAUD_RATE = 19200
RETRIEVES_COUNTER = 2
STATISTICS_TIMEOUT = 900

# For Dev:
USB_PORT = "COM3"
BACKEND_URL = 'http://host.docker.internal:8000/'


# For Prod:
# BACKEND_URL = 'http://localhost:8000/'
# USB_PORT = "/dev/ttyUSB1"

def read_till_timeout(serial_connection, term):
    matcher = re.compile(term)
    tic = time.time()
    buff = serial_connection.read(128)
    while ((time.time() - tic) < SERIAL_TIMEOUT) and (not matcher.search(buff)):
        buff += serial_connection.read(128)
    return buff


if __name__ == '__main__':
    hives = None

    while not hives:
        try:
            data = requests.get(BACKEND_URL + 'hives')
            hives = data.json()
        except requests.exceptions.ConnectionError as exception:
            print(exception)
            time.sleep(60)

    while True:
        print('\nBegin, timeout: ', STATISTICS_TIMEOUT / 60, 'min')
        print('Time Kyiv:', datetime.now(tz=timezone('Europe/Kiev')).strftime("%Y-%m-%d %H:%M:%S"))

        for hive in hives:

            humidity = 0
            temperature = 0
            weight = 0

            try:

                ser = serial.Serial(USB_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                counter = 0

                while True:
                    counter += 1
                    print("\nWaiting for: ", str(hive["id"]))
                    request = 'D;0' + str(hive["id"]) + ';'
                    time.sleep(0.05)
                    print("Command sent: ", request)
                    ser.write(str.encode(request))
                    response_string = read_till_timeout(ser, term='\n').decode('utf-8').strip()

                    if len(response_string) > 5:
                        print("Response: ", response_string)
                        response = response_string.split(';')
                        for data in response:
                            if data[0] == "H":
                                humidity = data[2:]
                            if data[0] == "T":
                                temperature = data[2:]
                            if data[0] == "W":
                                weight = data[2:]

                        print('Temp:', temperature)
                        print('Weight:', weight)
                        print('Hum:', humidity)

                        json_data = {
                            "hive_id": hive["id"],
                            "temperature": temperature,
                            "humidity": humidity,
                            "weight": weight,
                            "avr_sound": 0,
                            "pressure": 0
                        }
                        x = requests.post(BACKEND_URL + 'statistic', params=json_data)
                        break
                    else:
                        print("No response from hive with id: ", hive["id"])
                        if counter >= RETRIEVES_COUNTER:
                            break
                ser.close()

            except (serial.SerialException,
                    requests.exceptions.ConnectionError) as exception:
                print(exception)

        time.sleep(STATISTICS_TIMEOUT)
