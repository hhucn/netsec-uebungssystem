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
            ['python', '-m', 'netsecus', 'client', '--help'], cwd=root_dir))
        self._test_output(subprocess.check_output(
            ['python', '-m', 'netsecus', 'server', '--help'], cwd=root_dir))

if __name__ == '__main__':
    unittest.main()
