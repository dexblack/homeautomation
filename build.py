import logging

class Build:
    def __init__(self, data):
        self.data = data
        self.control_by_name = {}
        self.control_pins_by_cid = {}
        self.organize_controls()
        self.organize_control_pins()

    def organize_controls(self):
        """
        Gather controls by cid.
        """
        for control_group in self.data["controls"]:
            row_start = control_group["row"] - 1  # Adjust for 0-based indexing
            for row_index, row in enumerate(control_group["rows"], start=row_start):
                for column_index, input_control in enumerate(row, start=1):
                    control_type_prefix = self.data["control types"][input_control["type"]]
                    cid = f"{control_type_prefix}{row_index + 1}_{column_index}"
                    self.control_by_name[input_control["name"]] = {
                        "cid": cid, "type": input_control["type"]
                    }

    def organize_control_pins(self):
        """
        Gather control pins by cid.
        """
        for device in self.data["I2C Config"]["devices"]:
            for pin_index, pin in enumerate(device["config"]["pins"], start=0):
                if pin["cid"] in self.control_pins_by_cid:
                    self.control_pins_by_cid[pin["cid"]]["pins"].append(pin_index)
                else:
                    self.control_pins_by_cid[pin["cid"]] = {
                        "address": device["address"],
                        "pins": [pin_index]
                    }

    def process_action(self, action, human_readable):
        """
        Process actions and generate script steps.
        """
        steps = []
        # Iterate through the data extracting the action's I/O events.
        for description in action.keys():
            for io_event in action[description]:
                self.process_io_event(io_event, steps, human_readable)
        return steps

    def process_io_event(self, io_event, steps, human_readable):
        for control_name in io_event.keys():
            if not self.validate_control(control_name, io_event):
                continue

            input_control, input_cfg = self.get_input_control_and_cfg(control_name)
            output_control_name, output_control, output_cfg = self.get_output_control_and_cfg(control_name, io_event)
            if not input_control or not input_cfg or \
            not output_control_name or not output_control or not output_cfg:
                continue

            if not self.validate_input_pins(input_cfg["pins"], io_event[control_name]["value"]) or \
                not self.validate_output_pins(output_cfg["pins"], io_event[control_name][output_control_name]):
                continue

            steps.append(self.generate_describe_or_script_step(
                control_name, io_event, input_cfg,
                output_control_name, output_cfg, human_readable))

    def validate_control(self, control_name, io_event):
        """
        Validate control existence and configuration.
        """
        if control_name not in self.control_by_name:
            logging.debug(f"{control_name} not found in configured controls.")
            return False
        return True

    def get_input_control_and_cfg(self, control_name):
        """
        Retrieve input control and configuration.
        """
        input_control = self.control_by_name.get(control_name)
        input_cfg = self.control_pins_by_cid.get(input_control["cid"])
        if not input_cfg:
            logging.debug(f"{input_control['cid']} not configured on any controller.")
            return None, None
        return input_control, input_cfg

    def get_output_control_and_cfg(self, control_name, io_event):
        """
        Retrieve output control, name, and configuration.
        """
        output_control_name = next((k for k in io_event[control_name].keys() if k != "value"), None)
        if not output_control_name:
            logging.debug(f"No output control specified for {control_name}.")
            return None, None, None
        output_control = self.control_by_name.get(output_control_name)
        output_cfg = self.control_pins_by_cid.get(output_control["cid"])
        if not output_cfg:
            logging.debug(f"{output_control['cid']} not configured on any controller.")
            return None, None, None
        return output_control_name, output_control, output_cfg

    def validate_input_pins(self, pins, value):
        """
        Validate input pins against value.
        """
        if not self.valid_pins_value(pins, value):
            logging.error("Input value exceeds pin capacity.")
            return False
        return True

    def validate_output_pins(self, pins, value):
        """
        Validate output pins against value.
        """
        if not self.valid_pins_value(pins, value):
            logging.error("Output value exceeds pin capacity.")
            return False
        return True

    def generate_describe_or_script_step(self, control_name, io_event, input_cfg, output_control_name, output_cfg, human_readable):
        """
        Generate describe and script step based on input parameters.
        """
        if human_readable:
            description = f"if {control_name}=={io_event[control_name]['value']} then set {output_control_name} = {io_event[control_name][output_control_name]}"
            return {"respond": description}

        return {
            "in_address": input_cfg["address"],
            "in_pins": input_cfg["pins"],
            "in_value": io_event[control_name]["value"],
            "out_address": output_cfg["address"],
            "out_pins": output_cfg["pins"],
            "out_value": io_event[control_name][output_control_name]
        }

    @staticmethod
    def valid_pins_value(pins, value):
        """
        Verify sufficient pins to hold integer value.
        """
        return value < 2 ** len(pins)

    def __call__(self, human_readable=False):
        script = []
        for action in self.data["actions"]:
            script.append({"steps": self.process_action(action, human_readable)})

        return {"script": script}
