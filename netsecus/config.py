from __future__ import unicode_literals

import errno
import json


class Config(object):
    def __init__(self, default_cfg, site_cfg):
        self.default_cfg = default_cfg
        self.site_cfg = site_cfg

    def resolve(self, cfg, path):
        res = cfg
        for p in path:
            res = res[p]
        return res

    def __call__(self, path_str):
        path = path_str.split('.')
        try:
            return self.resolve(self.site_cfg, path)
        except KeyError:
            pass
        try:
            return self.resolve(self.default_cfg, path)
        except KeyError:
            raise KeyError('Missing configuration %s' % path_str)

    @staticmethod
    def _read_file(fn, default=None):
        try:
            with open(fn) as config_file:
                return json.load(config_file)
        except IOError as ioe:
            if ioe.errno == errno.ENOENT:
                if default is not None:
                    return default
            raise

    @classmethod
    def read(cls, default_path, site_path):
        return cls(cls._read_file(default_path), cls._read_file(site_path, {}))
