import time
import minimalmodbus
import serial
import requests

CREATE_NEW_DB = False
USB_PORT = "/dev/ttyUSB0"
# BACKEND_URL = 'http://host.docker.internal:8000/'
# For Prod:
BACKEND_URL = 'http://localhost:8000/'

TEMPERATURE_INT_REGISTER = 1
TEMPERATURE_DECIMAL_REGISTER = 2
WEIGHT_INT_REGISTER = 3
WEIGHT_DECIMAL_REGISTER = 4
HUMIDITY_REGISTER = 5

if __name__ == '__main__':

    data = requests.get(BACKEND_URL + 'hives')
    hives = data.json()

    while True:
        statistics = []
        for hive in hives:
            # number of decimals for storage
            decimal_number = 0
            try:

                instrument = minimalmodbus.Instrument(USB_PORT, hive["id"])
                instrument.serial.baudrate = 9600
                instrument.serial.timeout = 0.2
                print('Hive.id: ', hive["id"])

                # Write data if needed
                # instrument.write_register(1, 1, 0)

                # Read values
                print(instrument)
                print("-------------Test run--------------")

                temperature_int = instrument.read_register(TEMPERATURE_INT_REGISTER, decimal_number)
                temperature_decimal = instrument.read_register(TEMPERATURE_DECIMAL_REGISTER, decimal_number)
                weight_int = instrument.read_register(WEIGHT_INT_REGISTER, decimal_number)
                weight_decimal = instrument.read_register(WEIGHT_DECIMAL_REGISTER, decimal_number)
                humidity = instrument.read_register(HUMIDITY_REGISTER, decimal_number)

                temperature = temperature_int + temperature_decimal / 100
                weight = weight_int + weight_decimal / 100

                print('Temp:', temperature)
                print('Weight:', weight)
                print('Hum:', humidity)

                instrument.serial.close()

                json_data = {
                    "hive_id": hive["id"],
                    "temperature": temperature,
                    "humidity": humidity,
                    "weight": weight,
                    "avr_sound": 0,
                    "pressure": 0
                }
                x = requests.post(BACKEND_URL + 'statistic', params=json_data)

            except (serial.SerialException, minimalmodbus.NoResponseError) as exception:
                print(exception)

        time.sleep(900)
