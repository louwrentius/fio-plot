#!/usr/bin/env python3
import unittest

from bench_fio.benchlib import (
    argparsing,
    defaultsettings,
    display,
    supporting
)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.settings = defaultsettings.get_default_settings()
        self.settings["target"] = ["device"]
        self.settings["type"] = ["directory"]
        self.tests = supporting.generate_test_list(self.settings)
        self.settings["output"] = "output_directory"

    def test_generate_benchmarks(self):
        self.assertEqual(len(supporting.generate_test_list(self.settings)), 98)

    def test_generate_benchmarks_big(self):
        self.settings["target"] = ["filea", "fileb", "filec", "filed"]
        self.settings["block_size"] = ["4k", "8k", "16k", "32k"]
        self.assertEqual(len(supporting.generate_test_list(self.settings)), 1568)

    def test_are_loop_items_lists(self):
        for item in self.settings["loop_items"]:
            result = self.settings[item]
            self.assertTrue(isinstance(result, list))

    def test_calculate_duration(self):
        self.assertEqual(
            display.calculate_duration(self.settings, self.tests), "1:38:00"
        )

    def test_generate_output_directory_regular(self):
        benchmark = self.tests[0]
        self.assertEqual(
            supporting.generate_output_directory(self.settings, benchmark),
            "output_directory/device/4k",
        )

    def test_generate_output_directory_mixed(self):
        self.settings["mode"] = ["rw"]
        self.settings["rwmixread"] = [75]
        self.settings["loop_items"].append("rwmixread")
        tests = supporting.generate_test_list(self.settings)
        benchmark = tests[0]
        self.assertEqual(
            supporting.generate_output_directory(self.settings, benchmark),
            "output_directory/device/rw75/4k",
        )

    def test_number_of_settings(self):
        filtered_settings = []
        for setting in self.settings.keys():
            if setting not in self.settings["filter_items"]:
                filtered_settings.append(str(setting))
        filtered_settings.sort()
        descriptions = list((argparsing.get_argument_description()).keys())
        descriptions.sort()
        self.assertEqual(len(filtered_settings), len(descriptions))


if __name__ == "__main__":
    unittest.main()
