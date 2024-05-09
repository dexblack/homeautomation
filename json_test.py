# test.py

from plistlib import InvalidFileException
import unittest
import configure


class TestConfigureFunctions(unittest.TestCase):

    def setUp(self):
        # Some constants
        self.test_schema = "test/data/script.schema.json"
        self.test_json = "test/data/home.config.json"
        self.test_json_max_pins = "test/data/home.config.max-pins.json"
        self.test_json_duped_pins = "test/data/home.config.duped-pins.json"

    def test_load(self):
        # Test loading configuration from a file
        config = configure.load(self.test_json)
        self.assertIsInstance(config, dict)

    def test_validatejson_schema(self):
        # Verify the test configuration against the config schema
        self.assertTrue(
            configure.validate_json(self.test_json, self.test_schema)
        )

    def test_validscript_schema(self):
        # Verify the build output
        config = configure.load(self.test_json)
        data = configure.build(config)
        valid_schema = configure.validate_schema(data, self.test_schema)
        self.assertTrue(valid_schema)

    def test_validscript_response(self):
        # Verify the build output
        config = configure.load(self.test_json)
        data = configure.build(config)
        self.assertTrue("script" in data)
        script = data["script"]
        self.assertIs(len(script), 2, "script actions != 2")
        self.assertIsInstance(script[0]["reactions"], list)
        self.assertIs(
            len(script[0]["reactions"]), 2, "script[0].reactions does not have 2 items"
        )
        self.assertIsInstance(script[0]["reactions"][1], object)
        self.assertIs(
            len(script[1]["reactions"]), 6, "script[1].reactions does not have 6 items"
        )
        self.assertIsInstance(script[1]["reactions"], list)
        self.assertIsInstance(script[1]["reactions"][5], object)

    def test_valid_human_response(self):
        # Verify the build output
        config = configure.load(self.test_json)
        data = configure.build(config, True)
        self.assertTrue("script" in data)
        script = data["script"]
        self.assertEqual(
            script[1]["reactions"][5]["respond"],
            "if Main Section LED==2 then set LED Strip 2 = 1",
        )

    def test_invalid_max_pins(self):
        # Verify the build output
        config = configure.load(self.test_json_max_pins)
        with self.assertRaises(InvalidFileException, msg="Expected InvalidFileException."):
            configure.validate(config)

    def test_invalid_duped_pins(self):
        # Verify the build output
        config = configure.load(self.test_json_duped_pins)
        with self.assertRaises(InvalidFileException, msg="Expected InvalidFileException."):
            configure.validate(config)


if __name__ == "__main__":
    unittest.main()
