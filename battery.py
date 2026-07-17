#!/usr/bin/env python3

import minimalmodbus, time, json, sys
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import * 
from MAGLabPyLib import MAGDaemon
import logging
@dataclass_json
@dataclass
class _MODBUS:
    port: str
    sid: int
    timeout: float
    baud: int

class BATTERY(MAGDaemon):
    @dataclass_json
    @dataclass
    class Config(MAGDaemon.Config):
        modbus: _MODBUS
        loglevel: Optional[str] = None

    def __init__(self):
        long_name = "maglab_battery"
        cfg_file_name = "battery"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG) # just for development
        self.set_config(long_name, cfg_file_name)
        super().__init__(long_name, cfg_file_name)
        self.config_log()
        self.instr = minimalmodbus.Instrument(
                self.config.modbus.port,
                self.config.modbus.sid)
        self.instr.serial.baudrate = self.config.modbus.baud
        self.instr.serial.timeout = self.config.modbus.timeout
        self.instr.serial.clear_buffers_before_each_transaction = False
        self.logger.debug("Exiting init function")

    def on_message(self, client, userdata, message):
        if message.topic in self.config.mqtt.data_sources:
            if message.topic.endswith("checkup_req"):
                self.logger.debug("Received checkup")
                self.checkup("checkup")
        else:
            self.logger.warning("Message not in data sources")

    def handle_modbus(self, fn, *params, **kwparams):
        tries = 5
        retval = None
        while tries > 0:
            tries -= 1
            try:
                retval = fn(*params, **kwparams)
                break
            except Exception as err:
                self.logger.warning(f"Caught exception in modbus processing")
                self.instr.serial.flush()
                self.instr.serial.reset_input_buffer()
                if tries <= 0:
                    raise
        return retval

    def checkup(self, subtopic):
        named_checks = {f"{self.config.name} {k}": v for (k, v) in self.checks.items()}
        self.last_checkup = time.time()
        named_checks["time"] = self.last_checkup
        if subtopic == "checkup":
            self.logger.info(f"Publishing {subtopic}: {named_checks}")
        else:
            self.logger.debug(f"Publishing {subtopic}: {named_checks}")
        self.publish(f"{self.config.name}/{subtopic}", json.dumps(named_checks))

    def main(self):
        self.logger.debug("Calling super main")
        super().main()
        self.logger.info("Starting main loop")
        self.loop_start()
        length = 1.0
        now = time.time()
        target_time = now + length
        wait_time = target_time - now
        while not self.exit_evt.wait(wait_time):
            """ do work here """
            fields = ["SOC", "Voltage"]
            reading = self.handle_modbus(self.instr.read_registers, 21, 2)
            new_checks = dict(zip(fields, reading))

            fields = [f"cell{i:02}" for i in range(0, 16)]
            reading = self.handle_modbus(self.instr.read_registers, 113, 16)
            new_checks.update(dict(zip(fields, reading)))
            
            now = time.time()
            try:
                new_checks["Time Since Last"] = now - self.last_checkup
            except AttributeError:
                pass
            self.checks = new_checks
            self.checkup("run")
            """ processing time... """
            target_time += length
            now = time.time()
            wait_time = target_time - now
            if wait_time <= 0.0:
                wait_time = 0.0

        return self.exit_code

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    battery = BATTERY()
    sys.exit(battery.main())
