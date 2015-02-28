from __future__ import unicode_literals

import os
import subprocess
import unittest

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSourceQuality(unittest.TestCase):
    def _test_output(self, output_bytes):
        outp = output_bytes.decode()  # Decode with default encoding!
        self.assertIn('help message', outp)

    def test_module_exec(self):
        self._test_output(subprocess.check_output(
            ['python', '-m', 'netsecus', '--help'], cwd=root_dir))

    def test_python_exec_file(self):
        self._test_output(subprocess.check_output(
            ['python', 'netsecus/__main__.py', '--help'], cwd=root_dir))

    def test_direct_exec_file(self):
        self._test_output(subprocess.check_output(
            ['netsecus/__main__.py', '--help'], cwd=root_dir))

    def test_direct_exec_dir(self):
        self._test_output(subprocess.check_output(
            ['python', 'netsecus', '--help'], cwd=root_dir))
        self._test_output(subprocess.check_output(
            ['python', 'netsecus/', '--help'], cwd=root_dir))


if __name__ == '__main__':
    unittest.main()
