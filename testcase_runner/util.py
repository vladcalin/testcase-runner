import os


def iter_directory_for_sourcefiles(dirname="."):
    """
    Iterates recursively in ``dirname`` in search of relevant sourcefiles (``.py`` extension
     and that does not start with ``"__"``).

    :param dirname: the name of the directory to search in. Defaults to current working directory
    :return: a generator that yields full file paths of source files.
    """
    dirname = os.path.abspath(dirname)
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
            yield os.path.join(root, filename)
