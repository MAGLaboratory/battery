import minimalmodbus
import time

instr = minimalmodbus.Instrument("/dev/ttyUSB1", 1)
instr.serial.baudrate = 9600

for i in range(0,15):
    if i < 14:
        print(instr.read_registers(i*10, 10))
    else:
        print(instr.read_registers(i*10, 4))
"""
while True:
    print(instr.read_register(21))
    time.sleep(1)
"""
