import logging
import json
from plistlib import InvalidFileException
import jsonschema


class Configure:
    def __init__(self, config_file):
        """
        Load JSON configuration file.
        """
        self.data = {}
        try:
            with open(config_file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"Configuration file '{config_file}' not found: {e}.")
            raise
        except json.decoder.JSONDecodeError as e:
            logging.error(f"Error decoding JSON in '{config_file}': {e}")
            raise

    def schema_is_valid(self, schema_file):
        """
        Validate loaded configuration against a JSON schema.
        """
        if not self.data:
            logging.error("No configuration data loaded.")
            return False

        try:
            with open(schema_file, "r") as f:
                schema = json.load(f)
            jsonschema.validate(self.data, schema)
            return True
        except FileNotFoundError:
            logging.error(f"Schema file '{schema_file}' not found.")
            return False
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"Schema validation failed: {e}")
            return False
        
    def is_valid(self):
        """
        Validate the loaded configuration.
        Assumes the schema has been checked already, so no extra checking for missing properties.
        """
        parent_keys = []
        # Checking for pin value exceeding maxpins specification
        # and duplicate pins within a device connections specification.
        for device_index, device in enumerate(self.data["I2C Config"]["devices"]):
            parent_keys.append(f"I2C Config.devices[{device_index}]")
            maxpins = device["maxpins"]
            pins = {}
            for pin_index, pin in enumerate(device["config"]["pins"]):
                parent_keys.append(f"config.pins[{pin_index}]")
                pin_number = str(pin["pin"])
                if pin_number in pins:
                    raise InvalidFileException(f"Duplicate pin: {".".join(parent_keys)} cid = {pin["cid"]} pin = {pin["pin"]}")
                pins[pin_number] = 1
                if pin["pin"] > maxpins-1:
                    raise InvalidFileException(f"Pin number exceeded max: {".".join(parent_keys)} cid = {pin["cid"]} pin = {pin["pin"]} > {maxpins-1}")
                parent_keys.pop()  # Remove "device[index]" from parent keys
            parent_keys.pop()  # Remove "device[index]" from parent keys


    def report(config):
        """
        Print the configuration report.
        """
        for key, value in config.items():
            if key not in [
                "microcontroller",
                "control types",
                "NeoPixels",
                "IC2 Config",
            ]:  # Exclude for brevity
                logging.info(f"{key}: ", value)

    def __call__(self):
        return self.data
