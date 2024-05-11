# main.py

import os
from configure import Configure
from build import Build
import generate
import logging

def main():
    # Calculate the path to home.config.json based on the location of this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file_path = os.path.join(script_dir, 'test', 'data', 'config.schema.json')
    config_file_path = os.path.join(script_dir, 'test', 'data', 'home.config.json')
    
     # Validate the loaded configuration
    try:
        configure = Configure(config_file_path)
        assert(configure.schema_is_valid(schema_file_path))

        # Load configuration from the calculated path
        configure.report()
        logging.info("Configuration is valid.")
    except ValueError as e:
        logging.debug(f"Configuration validation failed: {e}")

    ui = generate.ui(configure())
    logging.info(ui)
    return

    actions = Build(configure()).build()
    schema_file_path = os.path.join(script_dir, 'test', 'data', 'script.schema.json')
    assert(configure.validate_schema(actions, schema_file_path))

    # Report the loaded configuration

if __name__ == "__main__":
    main()
