from __future__ import unicode_literals

import io
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSourceQuality(unittest.TestCase):

    def _test_unicode_literals(self, fn, code):
        if "'" not in code and '"' not in code:
            return
        self.assertRegexpMatches(
            code,
            r'''(?x)
            (?:(?:\#.*?|\s*)\n)*
            from\s+__future__\s+
            import\s+(?:[a-z_]+,\s*)*unicode_literals''',
            'unicode_literals import  missing in %s' % fn)

        m = re.search(r'(?<=\s)u[\'"](?!\)|,|$)', code)
        if m:
            self.assertFalse(
                m,
                'u present in %s, around %s' % (
                    fn, code[m.start() - 10:m.end() + 10]))

    def _test_regexp_rawstrings(self, fn, code):
        m = re.search(
            r're\.(?:search|match|findall|finditer)\(\s*["\']', code)
        if m:
            self.assertFalse(
                m,
                'Regular expression string not marked as raw string '
                'in %s, around %s' % (
                    fn, code[m.start() - 10:m.end() + 10]))

    def _test_strange_is(self, fn, code):
        ''' is tests whether two names refer to the same object.
        This is useful when the object is guaranteed to exist only once,
        as is the case with None.

        There is no such guarantee for integers (the behavior depends on the
        implementation). See http://stackoverflow.com/q/306313/35070 for
        more details.
        '''
        m = re.search(
            r'(?m)^\s*(.*?\s+is\s+[0-9]+.*?)\s*$', code)
        if m:
            self.assertFalse(
                m,
                'Very strange is comparison in %s, in line %r' % (
                    fn, m.group(1)))

    def _test_unnecessary_parens(self, fn, code):
        ''' Instead of while(True): , which looks like C code, in Python we can
        dispose of the parentheses and simply write while True:'''
        m = re.search(
            r'(?m)^\s*(if|while)\((.{,20})\):\s*$', code)
        if m:
            self.assertFalse(
                m,
                'Are the parentheses in line %r in file %s really necessary? '
                'How about  %s %s:  ?' % (
                    m.group(0), fn, m.group(1), m.group(2)))

    def _test_weird_constants(self, fn, code):
        ''' Constants for string indexing should be calculated with len so it
        is obvious what happens. If possible, try to use proper parsing. '''
        m = re.search(
            r'\[([3-9]|[1-9][0-9]{1,})[:\]]', code)
        if m:
            self.assertFalse(
                m,
                'Strange constant %s in file %s, around "%s". '
                'Can we use len instead?' % (
                    m.group(1), fn, code[m.start() - 40:m.end() + 1]
                ))

    def test_all_files(self):
        for dirpath, _, filenames in os.walk(root_dir):
            for basename in filenames:
                if not basename.endswith('.py'):
                    continue

                fn = os.path.join(dirpath, basename)
                with io.open(fn, encoding='utf-8') as inf:
                    code = inf.read()

                self._test_unicode_literals(fn, code)
                self._test_regexp_rawstrings(fn, code)
                self._test_strange_is(fn, code)
                self._test_unnecessary_parens(fn, code)
                self._test_weird_constants(fn, code)

if __name__ == '__main__':
    unittest.main()
