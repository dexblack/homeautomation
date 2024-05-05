import json

def load(file_path):
    """
    Load configuration from a JSON file.
    """
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def validate(config, parent_keys=None):
    """
    Validate the configuration format.
    """
    if parent_keys is None:
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
                        print(f"Control: {control_name} at {'.'.join(parent_keys)}")

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
            print(f"{key}: {value}")

def build(config):
    """
    Build something based on the configuration.
    """
    # Placeholder for build process
    pass

def generate(config):
    """
    Generate something based on the configuration.
    """
    # Placeholder for generate process
    pass
