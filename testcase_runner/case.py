from testcase_runner.errors import TestcaseInitError


class TestCaseResult:
    def __init__(self, test_case, passed, time_elapsed, exception, actual_result):
        self.test_case = test_case
        self.passed = passed
        self.time_elapsed = time_elapsed
        self.exception = exception
        self.actual_result = actual_result

    def __repr__(self):
        return str(self.__dict__)


class FunctionTestCase:
    def __init__(self, function_to_run, author, expected_result=None, check_function=None):
        self.to_run = function_to_run
        self.author = author
        if not expected_result and not check_function:
            raise TestcaseInitError("Only one of expected_result or check_function required. None given")
        if expected_result and check_function:
            raise TestcaseInitError("Only one of expected_result or check_function required. Both given")
        if check_function:
            self.check_func = check_function
        else:
            self.check_func = lambda *args, **kwargs: expected_result

    def run(self):
        pass
