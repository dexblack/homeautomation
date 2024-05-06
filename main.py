# main.py

import os
import configure
import logging

def main():
    # Calculate the path to home.config.json based on the location of this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file_path = os.path.join(script_dir, 'test', 'data', 'config.schema.json')
    config_file_path = os.path.join(script_dir, 'test', 'data', 'home.config.json')

    assert(configure.validate_json(config_file_path, schema_file_path))

    # Load configuration from the calculated path
    config = configure.load(config_file_path)
    
     # Validate the loaded configuration
    try:
        configure.validate(config)
        logging.info("Configuration is valid.")
    except ValueError as e:
        logging.debug(f"Configuration validation failed: {e}")

    actions = configure.build(config)

    # Report the loaded configuration
    configure.report(actions)

if __name__ == "__main__":
    main()
