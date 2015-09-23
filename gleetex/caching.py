"""This file contains the class for caching converted formulas to not convert a
formula twice."""

import json
import os

CACHE_VERSION = '2.0'

def unify_formula(formula):
    """This function unifies a formula. This e.g. means that multiple white
    spaces are squeezed into one and a tab will be replaced by a space. With
    this it is more realistic that a recurring formula in a document is detected
    as such, even though if it might have been written with different spacing.
    Replace {} by " " as well.
    :param formula input formula
    :return the modified formula"""
    return formula.replace('{}', ' ').replace('\t', ' ').replace('  ', ' '). \
        rstrip().lstrip()

class ImageCache:
    VERSION_STR = 'GladTeX__cache__version'
    def __init__(self, path='gladtex.cache'):
        self.__cache = {}
        self.__set_version(CACHE_VERSION)
        self.__path = path
        if os.path.exists(path):
            self._read()

    def __contains__(self, formula):
        """Check whether given formula is already in cache. Formulas are unified
        using `unify_formula`."""
        return unify_formula(formula) in self.__cache.keys()

    def __len__(self):
        """Remove number of entries in cache."""
        # ignore version
        return len(self.__cache) - 1

    def __set_version(self, version):
        """Set version of cache (data structure format)."""
        self.__cache[ImageCache.VERSION_STR] = version

    def write(self):
        """Write cache to disk. The file name will be the one configured during
        construction of the cache. This method is intended for internal use."""
        with open(self.__path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.__cache))

    def _read(self):
        """Read JSon from disk into cache, if file exists."""
        if os.path.exists(self.__path):
            with open(self.__path, 'r', encoding='utf-8') as file:
                self.__cache = json.load(file)
        if not isinstance(self.__cache, dict):
            raise ValueError("Decoded JSon is not a dictionary.")
        if not self.__cache.get(ImageCache.VERSION_STR):
            self.__set_version(CACHE_VERSION)
        cur_version = self.__cache.get(ImageCache.VERSION_STR)
        if cur_version != CACHE_VERSION:
            raise ValueError("Cache in %s has version %s, expected %s." % \
                    (self.__path, cur_version, CACHE_VERSION))

    def add_formula(self, formula, pos, file_path):
        """Add formula to cache. The cache consists of a mapping from formula to
        (pos, file path). Formulas are "unified" with `unify_formula`. Existing
        formulas are overwritten.
        :param formula formula to add
        :pos positioning information (dictionary with keys height, width and
                depth)
        :param file_path path to image file which contains the formula.
        :raises OSError if specified image doesn't exists"""
        if not pos or not formula or not file_path:
            raise ValueError("the supplied arguments may not be empty/none")
        if not os.path.exists(file_path):
            raise OSError("cannot add %s to the path: doesn't exist" %
                    file_path)
        formula = unify_formula(formula)
        self.__cache[formula] = {'pos' : pos, 'path' : file_path}

    def remove_formula(self, formula):
        """Formula is unified using `unify_formula` and removed. If no such
        formula was found, a KeyError is raised."""
        formula = unify_formula(formula)
        if not formula in self.__cache:
            raise KeyError("key %s not in cache" % formula)
        else:
            del self.__cache[formula]

    def get_formula_data(self, formula):
        """Return positioning info (dict) and path to image for given formula or
        raise ValueError if not found."""
        formula = unify_formula(formula)
        if not formula in self.__cache:
            raise KeyError(formula)
        else:
            return (self.__cache[formula]['pos'], self.__cache[formula]['path'])

