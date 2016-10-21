from testcase_runner.util import iter_directory_for_sourcefiles
from testcase_runner.function_util import FunctionDiscoveryStrategy, FunctionTestCase


class TestRunner:
    def __init__(self, source_files, discovery_strategies, test_cases):
        self.source_files = self.__validate_iterable(source_files, "source_files")
        self.discovery_strategies = self.__validate_iterable(discovery_strategies, "discovery_strategies")
        self.__validate_iterable(test_cases, "test_cases")
        self.discovery_strategies = discovery_strategies
        self.test_cases = test_cases
        self.items = {}

        self.initialize_context()
        print(self.items)

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


if __name__ == '__main__':
    TestRunner(iter_directory_for_sourcefiles("test_data"), [FunctionDiscoveryStrategy()], ["a"])
