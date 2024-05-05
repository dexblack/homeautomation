# main.py

import os
import configure

def main():
    # Calculate the path to home.config.json based on the location of this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(script_dir, 'test', 'data', 'home.config.json')

    # Load configuration from the calculated path
    config = configure.load(config_file_path)
    
     # Validate the loaded configuration
    try:
        configure.validate(config)
        print("Configuration is valid.")
    except ValueError as e:
        print(f"Configuration validation failed: {e}")

    # Report the loaded configuration
    configure.report(config)

if __name__ == "__main__":
    main()
