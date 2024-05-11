def ui(config):
    """
    Construct from a JSON based configuration object.
    """
    # Initialize an empty sparse array
    sparse_array = []

    # Get the control types mapping
    control_types = config.get("control types", {})

    # Iterate through the controls
    for control in config.get("controls", []):
        # Iterate through the rows
        group = control["group"]
        for row_index, row in enumerate(control["rows"], start=control["row"]):
            # Initialize a group-specific row
            group_row = []
            for col_index, col in enumerate(row, start=1):
                name = col.get("name")
                if col["type"] == "null":
                    continue
                # Construct the sparse array entry
                entry = {
                    "row": row_index,
                    "col": col_index,
                    "cid": f"{control_types.get(col.get("type"), '')}{row_index}_{col_index}",
                    "name": name,
                }
                group_row.append(entry)
            # Append the group-specific row to the sparse array
            sparse_array.append({ "group": group, "rows": group_row })

    return sparse_array
