import logging
import json
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
