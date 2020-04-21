#!/usr/bin/env python3
import unittest
import importlib
import bench_fio as b


class TestFunctions(unittest.TestCase):

    def setUp(self):
        self.settings = b.get_default_settings()
        self.settings['target'] = ['device']
        self.tests = b.generate_test_list(self.settings)
        self.settings['output'] = 'output_folder'

    def test_generate_benchmarks(self):
        self.assertEqual(len(b.generate_test_list(self.settings)), 98)

    def test_generate_benchmarks_big(self):
        self.settings['target'] = ['a', 'b', 'c', 'd']
        self.settings['block_size'] = ['a', 'b', 'c', 'd']
        self.assertEqual(len(b.generate_test_list(self.settings)), 1568)

    def test_are_loop_items_lists(self):
        for item in self.settings['loop_items']:
            result = self.settings[item]
            self.assertTrue(isinstance(result, list))

    def test_calculate_duration(self):
        self.assertEqual(b.calculate_duration(
            self.settings, self.tests), '1:38:00')

    def test_generate_output_folder_regular(self):
        benchmark = self.tests[0]
        self.assertEqual(b.generate_output_folder(
            self.settings, benchmark), 'output_folder/device/4k')

    def test_generate_output_folder_mixed(self):
        self.settings['mode'] = ['rw']
        tests = b.generate_test_list(self.settings)
        benchmark = tests[0]
        self.assertEqual(b.generate_output_folder(
            self.settings, benchmark), 'output_folder/device/rw75/4k')


if __name__ == '__main__':
    unittest.main()
