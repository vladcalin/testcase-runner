import inspect

from testcase_runner.base import DiscoveryStrategy, TestCase, CaseRun


class FunctionDiscoveryStrategy(DiscoveryStrategy):
    def discover_from_sourcefile(self, source_file):
        module = self.load_module_from_filename_with_timeout(source_file)
        if not module:
            print("Module not loaded")
            return None, []

        if not hasattr(module, "__author__"):
            print("Module {} has no __author__".format(source_file))
            return None, []

        author = getattr(module, "__author__")

        items = []
        for item_name in dir(module):
            if item_name.startswith("__"):
                continue

            current_item = getattr(module, item_name)
            if inspect.isfunction(current_item):
                items.append(current_item)
        return author, items


class FunctionTestCase(TestCase):
    def __init__(self, function_name, args, kwargs, verify_result=None, expected_result=None, timeout=15):
        self.function_name = function_name
        self.args = args
        self.kwargs = kwargs
        self.timeout = timeout

        if verify_result is None and expected_result is None:
            raise ValueError("One of verify_result and expected_result is mandatory. Provided none.")

        if verify_result is not None and expected_result is not None:
            raise ValueError("One of verify_result and expected_result is mandatory. Provided both.")

        if expected_result:
            self.verify_result = lambda *a, **k: expected_result
        else:
            self.verify_result = verify_result


class FunctionRun(CaseRun):
    def __init__(self, author, function, test_case):
        self.test_case = test_case
        self.author = author
        self.function = function
        self.test_case = test_case

    def run(self):
        print("User: {}; Function: {}; args: {}; kwargs: {}".format(self.author, self.function, self.test_case.args,
                                                                    self.test_case.kwargs))


if __name__ == '__main__':
    strategy = FunctionDiscoveryStrategy()
    author, items = strategy.discover_from_sourcefile(r"D:\Projects\testcase-runner\testcase_runner\test_data\test2.py")

    case1 = FunctionTestCase("my_sum", (1, 2, 3), {}, expected_result=6)
    case2 = FunctionTestCase("my_sum", (), {}, expected_result=0)
    case3 = FunctionTestCase("my_sum", (-1, 0, 1), {}, expected_result=0)
    case4 = FunctionTestCase("my_sum", tuple(range(0, 100)), {}, expected_result=4950)

    cases = [case1, case2, case3, case4]

    for item in items:
        for case in cases:
            if item.__name__ == case.function_name:
                FunctionRun(author, item, case).run()
