import os

from testcase_runner.util import iter_directory_for_sourcefiles
from testcase_runner.function_util import FunctionDiscoveryStrategy, FunctionTestCase


class TestRunner:
    def __init__(self, target):
        if os.path.isdir(target):
            self.source_files = iter_directory_for_sourcefiles(target)
        elif os.path.isfile(target):
            self.source_files = [target]
        else:
            raise ValueError("Unable to find {}".format(target))

        self.discovery_strategies = []
        self.test_cases = []
        self.items = {}
        self._initialized = False

    def add_discovery_strategy(self, strategy):
        if strategy not in self.discovery_strategies:
            self.discovery_strategies.append(strategy)

    def add_test_case(self, test_case):
        if test_case not in self.test_cases:
            self.test_cases.append(test_case)

    def initialize_context(self):
        for strategy in self.discovery_strategies:
            for source_file in self.source_files:
                author, items = self.get_items_from_strategy(source_file, strategy)
                if not author or not items:
                    print("Failed to extract items from strategy {} ({})".format(strategy, source_file))
                    continue
                if author not in self.items:
                    self.items[author] = items
                else:
                    self.items[author].extend(items)
        self._initialized = True

    def __validate_iterable(self, iterable, name):
        try:
            result = list(iterable)
        except (ValueError, TypeError):
            raise TypeError("{} must be list or tuple, got {} instead".format(name,
                                                                              type(iterable).__name__))
        else:
            return result

    def get_items_from_strategy(self, sourcefile, strategy):
        return strategy.discover_from_sourcefile(sourcefile)

    def run_cases(self):
        if not self._initialized:
            raise RuntimeError("Runner not initialized.")


if __name__ == '__main__':
    TestRunner(iter_directory_for_sourcefiles("test_data"), [FunctionDiscoveryStrategy()], ["a"])
