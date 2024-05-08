import json
import jsonschema
import logging

def load(file_path):
    """
    Load configuration from a JSON file.
    """
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def validate_schema(data, schema_file):
        # Validate JSON data against schema
    try:
        # Load JSON schema from file
        with open(schema_file, 'r') as f:
            schema = json.load(f)
            jsonschema.validate(data, schema)

        logging.info("Validation successful: JSON file is valid according to the schema.")
        return True
    
    except jsonschema.exceptions.ValidationError as e:
        logging.error("Validation failed:", e)
        return False

def validate_json(json_file, schema_file):
    """
    Validate a JSON file against a JSON schema.

    Args:
        json_file (str): Path to the JSON file to validate.
        schema_file (str): Path to the JSON schema file.

    Returns:
        bool: True if the JSON file is valid according to the schema, False otherwise.
    """
    # Load JSON data from file
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    return validate_schema(json_data, schema_file)

def validate(config):
    """
    Validate the configuration format.
    """
    parent_keys = []

    # Validation rules implementation
    unique_names = set()
    control_names = set()
    control_types = config.get("control types", {})
    controls = config.get("controls", [])
    
    # Validate control names uniqueness and generate control names list
    for control_group_index, control_group in enumerate(controls, start=1):
        parent_keys.append(f"controls[{control_group_index - 1}]")

        for row_index, row in enumerate(control_group.get("rows", []), start=1):
            parent_keys.append(f"rows[{row_index - 1}]")
            
            for column_index, column in enumerate(row, start=1):
                parent_keys.append(f"control[{column_index - 1}]")
                try:
                    name = column["name"]
                except KeyError:
                    raise ValueError(f"Missing 'name' field at {'.'.join(parent_keys)}")
                
                if name in unique_names:
                    raise ValueError(f"Duplicate control name found: {name} at {'.'.join(parent_keys)}")
                else:
                    unique_names.add(name)
                
                control_type = column.get("type", "")
                if control_type not in control_types:
                    raise ValueError(f"Invalid control type: {control_type} at {'.'.join(parent_keys)}")
                else:
                    prefix = control_types[control_type]

                    if control_type != "null":
                        group_start_row = control_group.get("row", 0)
                        if group_start_row == 0:
                            raise ValueError(f"Missing 'row' field at {'.'.join(parent_keys)}")
                        
                        control_name = f"{prefix}{group_start_row + row_index}_{column_index}"
                        logging.trace(f"Control: {control_name} at {'.'.join(parent_keys)}")

                        if control_name in control_names:
                            raise ValueError(f"Duplicate control name found: {control_name} at {'.'.join(parent_keys)}")
                        else:
                            control_names.add(control_name)
                parent_keys.pop()  # Remove "control[index]" from parent keys
            parent_keys.pop()  # Remove "rows[index]" from parent keys
        parent_keys.pop()  # Remove "controls[index]" from parent keys
    
    # Additional schema validation can be implemented here
    return True  # Configuration is valid

def report(config):
    """
    Print the configuration report.
    """
    for key, value in config.items():
        if key not in ["microcontroller", "control types", "NeoPixels", "IC2 Config"]:  # Exclude for brevity
            logging.info(f"{key}: ", value)

def build(data, human_readable=False):
    new_script = []
    control_by_name = {}
    control_pins_by_cid = {}

    # Organize controls by cid
    for control_group in data["controls"]:
        row_start = control_group["row"] - 1  # Adjust for 0-based indexing
        for row_index, row in enumerate(control_group["rows"], start=row_start):
            for column_index, input_control in enumerate(row, start=1):
                control_type_prefix = data["control types"][input_control["type"]]
                cid = f"{control_type_prefix}{row_index + 1}_{column_index}"
                control_by_name[input_control["name"]] = {
                    "cid": cid, "type": input_control["type"]
                }

    for device in data["I2C Config"]["devices"]:
        for pin in device["config"]["pins"]:
            if pin["cid"] in control_pins_by_cid:
                control_pins_by_cid[pin["cid"]]["pins"].append(pin["pin"])
            else:
                control_pins_by_cid[pin["cid"]] = {
                    "address": device["address"],
                    "pins": [ pin["pin"] ]
                }

    def valid_pins_value(pins, value):
        # Verify sufficient pins to hold integer value
        return value < 2 ** len(pins)

    # Iterate through actions
    for action in data["actions"]:
        script = []
        for description in action.keys():
            for io_event in action[description]:
                for control_name in io_event.keys():
                    input_control = control_by_name[control_name]
                    if input_control["cid"] not in control_pins_by_cid:
                        logging.debug(f"{input_control["cid"]} not configured on any controller.")
                        continue

                    input_cfg = control_pins_by_cid[input_control["cid"]]
                    output_control_name = next(k for k in io_event[control_name].keys() if k != "value")
                    output_control = control_by_name[output_control_name]
                    output_cfg = control_pins_by_cid[output_control["cid"]]

                    assert(valid_pins_value(input_cfg["pins"], io_event[control_name]["value"]))
                    assert(valid_pins_value(output_cfg["pins"], io_event[control_name][output_control_name]))

                    describe = {
                        "respond": f"if {control_name}=={io_event[control_name]["value"]} then set {output_control_name} = {io_event[control_name][output_control_name]}"
                    }

                    script_step = {
                        "in_address": input_cfg["address"],
                        "in_pins": input_cfg["pins"],
                        "in_value": io_event[control_name]["value"],
                        "out_address": output_cfg["address"],
                        "out_pins": output_cfg["pins"],
                        "out_value": io_event[control_name][output_control_name]
                    }

                    script.append(describe if human_readable else script_step)

        new_script.append({"reactions": script})

    return {"script": new_script}

def generate(config):
    """
    Generate code to execute a polling script.
    """
    # Someday we may need to allow code to be inserted into the script steps.
    pass
