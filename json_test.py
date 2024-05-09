# test.py

from plistlib import InvalidFileException
import unittest
from configure import Configure
from build import Build

class TestConfigure(unittest.TestCase):

    def setUp(self):
        # Some constants
        self.test_json = 'test/data/home.config.json'
        self.test_json_max_pins = "test/data/home.config.max-pins.json"
        self.test_json_duped_pins = "test/data/home.config.duped-pins.json"

    def test_ctor(self):
        # Test loading configuration from a file
        config = Configure(self.test_json)
        self.assertIsInstance(config(), dict)

    def test_validate_json(self):
        # Verify the test configuration against the config schema
        config = Configure(self.test_json)
        self.assertTrue(config.schema_is_valid('test/data/config.schema.json'))

    def test_valid_script(self):
        # Verify the build output
        config = Configure(self.test_json)
        data = Build(config())()
        self.assertTrue("script" in data)
        script = data["script"]
        self.assertIs(len(script), 2, "script actions != 2")
        self.assertIsInstance(script[0]["steps"], list)
        self.assertIs(len(script[0]["steps"]), 2, "script[0].reactions does not have 2 items")
        self.assertIsInstance(script[0]["steps"][1], object)
        self.assertIs(len(script[1]["steps"]), 6, "script[1].reactions does not have 6 items")
        self.assertIsInstance(script[1]["steps"], list)
        self.assertIsInstance(script[1]["steps"][5], object)

    def test_valid_descript(self):
        # Verify the build output
        data = Build(Configure(self.test_json)())(human_readable=True)
        script = data["script"]
        self.assertTrue("script" in data)
        self.assertTrue(isinstance(script, list)) 
        self.assertIs(len(script), 2)
        self.assertTrue(isinstance(script[1], object))
        self.assertIs(len(script[0]["steps"]), 2)
        self.assertIs(len(script[1]["steps"]), 6)
        self.assertTrue(isinstance(script[1]["steps"], list))
        self.assertTrue(isinstance(script[1]["steps"][5]["respond"], str))
        self.assertEqual(script[1]["steps"][5]["respond"], 'if Main Section LED==2 then set LED Strip 2 = 1')

    def test_invalid_max_pins(self):
        # Verify the build output
        config = Configure(self.test_json_max_pins)
        self.assertRaises(InvalidFileException, config.is_valid)

    def test_invalid_duped_pins(self):
        # Verify the build output
        config = Configure(self.test_json_duped_pins)
        self.assertRaises(InvalidFileException, config.is_valid)
        
if __name__ == '__main__':
    unittest.main()
