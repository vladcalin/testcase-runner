import unittest
import os

from testcase_runner.test_runner import TestRunner
from testcase_runner.function_util import FunctionTestCase, FunctionDiscoveryStrategy
# from testcase_runner.class_util import ClassTestCase, ClassDiscoveryStrategy


class GeneralUnitTests(unittest.TestCase):
    def test_run_on_single_file(self):
        test_file = self._get_test_single_file()

        runner = TestRunner(test_file)

        # adding stategies
        runner.add_discovery_strategy(FunctionDiscoveryStrategy())
        # runner.add_discovery_strategy(ClassDiscoveryStrategy())

        # adding test cases
        runner.add_test_case(FunctionTestCase("my_sum", (1, 2, 3), {}, expected_result=6))
        runner.add_test_case(FunctionTestCase("my_sum", (), {}, expected_result=0))
        runner.add_test_case(FunctionTestCase("my_sum", tuple((x for x in range(100))), {}, expected_result=4950))

        runner.add_test_case(FunctionTestCase("my_prod", (1, 2, 3), {}, expected_result=6))
        runner.add_test_case(FunctionTestCase("my_prod", (0, 1, 2), {}, expected_result=0))

        runner.initialize_context()

    def _get_test_single_file(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_testfile1.py")


