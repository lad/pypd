#!/usr/bin/env python2.6

import unittest
import tempfile
import os
from contextlib import closing, contextmanager
import time
import pypd


class TestConfig(unittest.TestCase):

    SECTION = '[install]'
    KEYS = ['pd_root', 'key1', 'key2', 'key3']
    VALUES = ['/usr/bin', 'val1', 'val2', 'val3']
    KVS = zip(KEYS, VALUES)
    MKEYS = ['multkey', 'other_mult_key']
    MVALUES = [['val4', 'val5', 'val6'], ['val7', 'val8', 'val9', 'val10']]
    MKVS = zip(MKEYS, MVALUES)
    TEST_LINES = [SECTION] + \
                 ['%s=%s' % (k, v) for k, v in KVS] + \
                 ['%s_%d=%s' % (k, i + 1, v) for k, vals in MKVS \
                                          for i, v in enumerate(vals)]

    #self.assertRaises(StopIteration, next, iter(lst))

    @contextmanager
    def _new_cfg(self, *cfg_args, **cfg_kwargs):
        """Return a config object its mod-time and path (context manager)."""
        try:
            path = None
            fd, path = tempfile.mkstemp(text=True)

            if not cfg_kwargs.get('empty'):
                with closing(os.fdopen(fd, 'w')) as tmpfile:
                    tmpfile.write('\n'.join(self.TEST_LINES))

            mtime = os.path.getmtime(path)
            # Sleep a tiny amount so that subsequent changes will have a
            # different mtime than the mtime first reported here.
            time.sleep(0.02)

            if 'empty' in cfg_kwargs:
                del cfg_kwargs['empty']
            yield pypd.Config(path, *cfg_args, **cfg_kwargs), mtime, path
        finally:
            if path:
                os.unlink(path)

    def test_empty(self):
        with self._new_cfg(empty=True) as (cfg, mtime, path):
            cfg['key'] = 'val'
            # re-open to confirm the empty config was created correctly
            cfg = pypd.Config(path)
            self.assertTrue(cfg['key'] == 'val')

    def test_key_error(self):
        with self._new_cfg() as (cfg, mtime, path):
            self.assertRaises(KeyError, cfg.__getitem__, 'blah')
            self.assertRaises(KeyError, cfg.__delitem__, 'blah')

    def test_open_does_not_modify(self):
        with self._new_cfg(flush=True) as (_, mtime, path):
            self.assertTrue(mtime == os.path.getmtime(path))

    def test_flush_on_new_value(self):
        # Insert new value with flush on
        with self._new_cfg(flush=True) as (cfg, mtime, path):
            new_key, new_value = 'new_key', 'new_value'
            cfg[new_key] = new_value
            self.assertTrue(os.path.getmtime(path) > mtime)
            cfg2 = pypd.Config(path, flush=True)
            self.assertTrue(cfg2[new_key] == new_value)

        # Insert new value with flush off
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key, new_value = self.KEYS[0], 'some_new_value'
            old_value = cfg[key]
            cfg[key] = new_value
            self.assertTrue(os.path.getmtime(path) == mtime)
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == old_value)

        # Insert new value with flush off then turn on
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key, new_value = self.KEYS[0], 'some_new_value'
            old_value = cfg[key]
            cfg[key] = new_value
            self.assertTrue(os.path.getmtime(path) == mtime)

            # open a second config object and check the value hasn't changed
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == old_value)

            # This should cause the new value to be written
            cfg.flush = True
            self.assertTrue(os.path.getmtime(path) > mtime)
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == new_value)

    def test_flush_on_changed_value(self):
        # Change existin value with flush on
        with self._new_cfg(flush=True) as (cfg, mtime, path):
            key, new_value = self.KEYS[0], 'new_value'
            cfg[key] = new_value
            self.assertTrue(os.path.getmtime(path) > mtime)

            cfg2 = pypd.Config(path, flush=True)
            self.assertTrue(cfg2[key] == new_value)

        # Change existing value with flush off
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key, new_value = self.KEYS[0], 'new_value'
            old_value = cfg[key]
            cfg[key] = new_value
            self.assertTrue(os.path.getmtime(path) == mtime)

            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == old_value)

        # Change existing value with flush off then turn on
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key, new_value = self.KEYS[0], 'new_value'
            old_value = cfg[key]
            cfg[key] = new_value
            self.assertTrue(os.path.getmtime(path) == mtime)

            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == old_value)

            # This should cause the new value to be written
            cfg.flush = True
            self.assertTrue(os.path.getmtime(path) > mtime)
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2[key] == new_value)

    def test_flush_on_removed_value(self):
        # Delete value with flush on
        with self._new_cfg(flush=True) as (cfg, mtime, path):
            skey = self.KEYS[0]
            del cfg[skey]
            mkey = self.MKEYS[0]
            del cfg[mkey]
            self.assertTrue(os.path.getmtime(path) > mtime)

            cfg2 = pypd.Config(path, flush=True)
            self.assertTrue(cfg2.get(skey) == None)
            self.assertTrue(cfg2.get(mkey) == None)

        # Delete value with flush off
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key = self.KEYS[0]
            old_value = cfg[key]
            del cfg[key]
            self.assertTrue(os.path.getmtime(path) == mtime)
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2.get(key) == old_value)

        # Delete value with flush off then turn on
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            key = self.KEYS[0]
            old_value = cfg[key]
            del cfg[key]
            self.assertTrue(os.path.getmtime(path) == mtime)

            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2.get(key) == old_value)

            # This should cause the file to be written
            cfg.flush = True
            self.assertTrue(os.path.getmtime(path) > mtime)
            cfg2 = pypd.Config(path, flush=False)
            self.assertTrue(cfg2.get(key) == None)

    def test_get_set_single(self):
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            for key, value in self.KVS:
                self.assertTrue(cfg[key] == value)

            add_value = "...blah blah blah"
            for key, value in self.KVS:
                cfg[key] = value + add_value

            for key, value in self.KVS:
                self.assertTrue(cfg[key] == value + add_value)

    def test_get_set_multi(self):
        with self._new_cfg(flush=True) as (cfg, mtime, path):
            for mkey, mvalues in self.MKVS:
                self.assertTrue(cfg[mkey].sort() == mvalues.sort())

            mkvs = self.MKVS[:]
            mkvs[0][1].append('xxxval')
            mkvs[1][1].append('yyyval')
            mkvs.append(('third_mkey', ['thirdxx', 'thirdyy']))

            for mkey, mvalues in mkvs:
                cfg[mkey] = mvalues

            cfg = pypd.Config(path)
            for mkey, mvalues in mkvs:
                self.assertTrue(cfg[mkey].sort() == mvalues.sort())

    def test_delete(self):
        with self._new_cfg(flush=False) as (cfg, mtime, path):
            for key, value in self.KVS:
                self.assertTrue(cfg[key] == value)

            for key, _ in self.KVS:
                del cfg[key]

            for mkey, _ in self.MKVS:
                del cfg[mkey]

            for key, _ in self.KVS:
                self.assertFalse(cfg.get(key))
                self.assertRaises(KeyError, cfg.__getitem__, key)
                self.assertRaises(KeyError, cfg.__delitem__, key)
                self.assertFalse(cfg.delete(key))

            for mkey, _ in self.KVS:
                self.assertFalse(cfg.get(mkey))
                self.assertRaises(KeyError, cfg.__getitem__, mkey)
                self.assertRaises(KeyError, cfg.__delitem__, mkey)
                self.assertFalse(cfg.delete(mkey))
