import logging
import sys
import os
import hashlib
import threading
import inspect
import time
from collections import namedtuple

OUTPUT_HTML = 0
OUTPUT_JSON = 1

sys.dont_write_bytecode = True

Testcase = namedtuple("Testcase", "function args kwargs check_result")


class TestCaseRunner:
    def __init__(self, root_directory, enable_logging=False):
        self.logger = None
        self.root_directory = root_directory
        self.test_cases = []
        self.discovered = {}
        self.results = {}

        if enable_logging:
            self.enable_logging()
        else:
            self.logger = logging.Logger(__name__)
        self.logger.info("Initialized")
        self._discover_testcases()

    def run_cases(self):
        for author in self.discovered:
            self.logger.debug("Running for user {}".format(author))
            for testcase in self.test_cases:
                if self._author_has_function(author, testcase.function):
                    passed, runtime_secs, exception, result = self._run_single_case(
                        self.discovered[author][testcase.function],
                        testcase.args,
                        testcase.kwargs,
                        testcase.check_result
                    )
                    if author not in self.results:
                        self.results[author] = {}
                    self.results[author][testcase.function] = {
                        "args": testcase.args,
                        "kwargs": testcase.kwargs,
                        "passed": passed,
                        "runtime_secs": runtime_secs,
                        "exception": str(exception),
                        "result": result
                    }
                else:
                    self.results[author][testcase.function] = {
                        "args": testcase.args,
                        "kwargs": testcase.kwargs,
                        "passed": False,
                        "runtime_secs": 0.0,
                        "exception": str(NameError("Function {} not found".format(testcase.function))),
                        "result": None
                    }

    def _author_has_function(self, author, function_name):
        return function_name in self.discovered[author]

    def output_result(self, mode, stream):
        if mode == OUTPUT_JSON:
            import json
            stream.write(json.dumps(self.results, indent=4))

    def _run_single_case(self, func_to_run, args, kwargs, success_test):
        """
        Returns (passed, runtime_secs, exception, result)

        :param func_to_run:
        :param args:
        :param kwargs:
        :param success_test:
        :return:
        """

        class TestcaseRunThread(threading.Thread):
            def __init__(self):
                self.exception = None
                self.passed = False
                self.result = None
                super(TestcaseRunThread, self).__init__()

            def run(self):
                try:
                    result = func_to_run(*args, **kwargs)
                except Exception as e:
                    self.exception = e
                    self.passed = False
                else:
                    if not success_test(result):
                        self.passed = False
                        self.result = result
                        return
                    self.passed = True
                    self.result = result

        thread = TestcaseRunThread()
        thread.start()
        start_time = time.time()
        try:
            thread.join(15)
        except TimeoutError as e:
            return False, time.time() - start_time, e, None

        return thread.passed, time.time() - start_time, thread.exception, thread.result

    def _discover_testcases(self):
        for root, dirs, files in os.walk(self.root_directory):
            for filename in files:
                full_filename = os.path.join(root, filename)
                self.logger.info("Processing {}".format(full_filename))

                current_module = self.__load_module_from_filename_with_timeout(full_filename)
                if not current_module:
                    continue

                current_author = getattr(current_module, "__author__", None)
                self.logger.info("Author detected: {}".format(current_author))
                if not current_author:
                    self.logger.error("File {} has no defined __author__".format(full_filename))
                    continue

                if current_author not in self.discovered:
                    self.discovered[current_author] = {}

                extracted = self._extract_runnables(current_module)
                for func_name in extracted:
                    self.discovered[current_author][func_name] = extracted[func_name]

    def __load_module_from_filename_with_timeout(self, full_filename):

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

        thread = LoaderThread(full_filename)
        thread.start()
        try:
            thread.join(timeout=15)
        except TimeoutError:
            self.logger.error("Unable to load {}. Took more than 15 seconds".format(full_filename))
        else:
            return thread.module

    def _extract_runnables(self, module):
        to_return = {}
        for item_name in dir(module):
            if item_name.startswith("__"):
                continue

            item = getattr(module, item_name)
            if inspect.isfunction(item):
                to_return[item.__name__] = item
                self.logger.debug("Discovered {}".format(item.__name__))
        return to_return

    def enable_logging(self, level=logging.DEBUG):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s - %(funcName)s - %(levelname)s] - %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def define_testcase(self, function_name, check_result, *args, **kwargs):
        self.test_cases.append(
            Testcase(function=function_name, args=args, kwargs=kwargs, check_result=check_result)
        )
        self.logger.debug("Defined testcase {}".format(function_name))

        """

        runner = TestCaseRunner()

        runner.set_root_directory(".")
        runner.add_test_case("check_if_prime", 10)

        runner.run_cases(OUTPUT_HTML)

        How it works.

        Opens each file, aggregates all the testcases

        """


if __name__ == '__main__':
    pass
