import abc
import threading
import sys
import hashlib


class DiscoveryStrategy(metaclass=abc.ABCMeta):
    """
    Base class for item discovery strategy.
    """

    @abc.abstractmethod
    def discover_from_sourcefile(self, source_file):
        """
        Discovers and returns the targeted items from ``source_file``. Returns the author and a list of discovered
        items

        :param source_file: The path of the file to analyze and from which to extract items
        :return: a tuple (author, items) where author is a string and items is a list of discovered items. Returns
        ``None`` if the module import takes more than 15 seconds or the module does not have a defined ``__author__``
        """
        pass

    def load_module_from_filename_with_timeout(self, source_file):

        class LoaderThread(threading.Thread):

            def __init__(self, full_filename):
                super(LoaderThread, self).__init__()
                self.full_filename = full_filename
                self.module = None

            def run(self):
                if sys.version_info >= (3, 5):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(hashlib.md5(self.full_filename.encode()).hexdigest(),
                                                                  self.full_filename)
                    current_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(current_module)
                    self.module = current_module
                elif sys.version_info[:2] in ((3, 3), (3, 4)):
                    from importlib.machinery import SourceFileLoader
                    current_module = SourceFileLoader(hashlib.md5(self.full_filename.encode()).hexdigest(),
                                                      self.full_filename).load_module()
                    self.module = current_module
                else:
                    raise RuntimeError("Python version {} no supported. Use 3.3 or newer".format(sys.version_info))

        thread = LoaderThread(source_file)
        thread.start()
        try:
            thread.join(timeout=15)
        except TimeoutError:
            print("Unable to load {}".format(source_file))
        else:
            return thread.module


class TestCase(metaclass=abc.ABCMeta):
    """
    Base class for test cases. Defines how should an item be tested and how testing success is defined.
    """


class CaseRun(metaclass=abc.ABCMeta):
    """
    Base class for concrete item testing. Defines a concrete testing of an item, tested by a given TestCase's parameters
    """

    @abc.abstractmethod
    def run(self):
        """
        Runs the test case and returns the result represented by:

        - passed - if the test passed or not
        - args - the *args parameter
        - kwargs - the **kwargs parameter
        - result - the result of the tested item
        - expected_result - the expected result, if available
        - duration - how many seconds did it took for completion
        - error - if the function call raised an exception

        :return:
        """
        pass
