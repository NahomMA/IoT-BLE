import sys
import time
from argparse import ArgumentParser
from bluepy import btle  # linux only (no mac)



# BLE IoT Sensor Demo
# Author: Gary Stafford
# Reference: https://elinux.org/RPi_Bluetooth_LE
# Requirements: python3 -m pip install --user -r requirements.txt
# To Run: python3 ./rasppi_ble_receiver.py d1:aa:89:0c:ee:82 <- MAC address - change me!


def main():
    # get args
    args = get_args()
    print("Connecting...")
    Tempdic={}
    tmp=list([args.mac_address1,args.mac_address2])
    
    '''
    dc:61:e0:cc:a4:01   ------ ard1
    a1:a4:d1:a8:a3:aa  ------ ard2   
    '''
   
    print('to Mack add',tmp[0])
    nano_sense1 = btle.Peripheral(tmp[0])
    print("Discovering Services...")
    _ = nano_sense1.services
    environmental_sensing_service1 = nano_sense1.getServiceByUUID("181A")
    print("Discovering Characteristics...")
    _ = environmental_sensing_service1.getCharacteristics()



    print('to Mack add',tmp[1])
    nano_sense2 = btle.Peripheral(tmp[1])
    print("Discovering Services...")
    _ = nano_sense2.services
    environmental_sensing_service2 = nano_sense2.getServiceByUUID("A81A")
    print("Discovering Characteristics...")
    _ = environmental_sensing_service2.getCharacteristics()
    while True:
        print("\n")
     
     
        # print("--------------...........................................................")
        # print("......................1fst IoT Device.....................................")
        # print("--------------.............................................................")
       
        Tempdic["ard1"]=read_temperature(environmental_sensing_service1) 
        time.sleep(2)
        # print("--------------...........................................................")
        # print("--------------..........................................................")
        # print("--------------...........................................................")
        # print("......................2 nd IoT Device.....................................")
        # print("--------------.............................................................")
        # print("--------------.............................................................")
        # print("--------------..............................................................")

        Tempdic["ard2"]=read_temperature(environmental_sensing_service2)                
        time.sleep(2) # transmission frequency set on IoT device
        print(Tempdic)
def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes, in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232
    # print(f"{sys._getframe().f_code.co_name}: {value}")
    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little")
    return value


def split_color_str_to_array(value):
    # e.g., b'2660,2059,1787,4097\x00' -> 2660,2059,1787,4097 ->
    #       [2660, 2059, 1787, 4097] -> 166.0,128.0,111.0,255.0
    # print(f"{sys._getframe().f_code.co_name}: {value}")

    # remove extra bit on end ('\x00')
    value = value[0:-1]

    # split r, g, b, a values into array of 16-bit ints
    values = list(map(int, value.split(",")))

    # convert from 16-bit ints (2^16 or 0-65535) to 8-bit ints (2^8 or 0-255)
    # values[:] = [int(v) % 256 for v in values]

    # actual sensor is reading values are from 0 - 4097
    print(f"12-bit Color values (r,g,b,a): {values}")

    values[:] = [round(int(v) / (4097 / 255), 0) for v in values]

    return values


def byte_array_to_char(value):
    # e.g., b'2660,2058,1787,4097\x00' -> 2659,2058,1785,4097
    value = value.decode("utf-8")
    return value


def decimal_exponent_two(value):
    # e.g., 2350 -> 23.5
    return value / 100



def celsius_to_fahrenheit(value):
    return (value * 1.8) + 32

def read_temperature(service):
    temperature_char = service.getCharacteristics("2A6E")[0]
    temperature = temperature_char.read()
    temperature = byte_array_to_int(temperature)
    temperature = decimal_exponent_two(temperature)
    temperature = round(celsius_to_fahrenheit(temperature),2)
    return temperature
   


def get_args():
    arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
    arg_parser.add_argument('mac_address1', help="MAC address of device to connect")
    arg_parser.add_argument('mac_address2', help="MAC address of device to connect")
    args = arg_parser.parse_args()   
    return args


if __name__ == "__main__":
    main()