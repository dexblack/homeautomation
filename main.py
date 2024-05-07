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
    configure.report(config)
    
     # Validate the loaded configuration
    try:
        configure.validate(config)
        logging.info("Configuration is valid.")
    except ValueError as e:
        logging.debug(f"Configuration validation failed: {e}")

    logging.info(configure.build(config, True))
    actions = configure.build(config)
    schema_file_path = os.path.join(script_dir, 'test', 'data', 'script.schema.json')
    assert(configure.validate_json(actions, schema_file_path))

    # Report the loaded configuration

if __name__ == "__main__":
    main()
