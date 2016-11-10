from __future__ import print_function
import numpy as np
import unittest
from PyLHD.instruments import hdba_spec

class test_config(unittest.TestCase):
    def setUp(self):
        self.config = hdba_spec.Config()

    def test_no_shot(self):
        with self.assertRaises(ValueError):
            self.config._find_config_files(0)

    def test_find_shot(self):
        true_file = 'settings_125519.txt'
        test_shot = 129381
        self.config.read(test_shot)
        self.assertTrue(self.config.setting_file == true_file)
        test_shot = 129382
        self.config.read(test_shot)
        self.assertTrue(self.config.setting_file == true_file)

    def test_parser(self):
        parsed = hdba_spec.parse('1')
        self.assertTrue(parsed == 1)
        parsed = hdba_spec.parse('1.2')
        self.assertTrue(parsed == 1.2)
        parsed = hdba_spec.parse('1.2, 1.3, 1.5')
        self.assertTrue(parsed == [1.2, 1.3, 1.5])
        parsed = hdba_spec.parse('True')
        self.assertTrue(parsed == True)
        parsed = hdba_spec.parse('False')
        self.assertTrue(parsed == False)

    def test_setting(self):
        test_shot = 125520
        self.config.read(test_shot)
        # TODO test should be added.
        print(self.config.settings.Experiment.isexposuretimeinms)

if __name__ == '__main__':
     unittest.main()
