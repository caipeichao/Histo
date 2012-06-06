import unittest
from unittest import TestCase
from reader import reader
from writer import writer
from bundle.bundle import bundle
from files.files import files

class test(TestCase):
    def __init__(self,a):
        TestCase.__init__(self,a)
    
    def test_read(self):
        with self._reader(b'123') as f:
            assert f.read() == b'123'
    
    def test_double_read(self):
        with self._reader(b'1234') as f:
            assert f.read(3) == b'123'
            assert f.read(1) == b'4'
    
    def test_read_too_much(self):
        with self._reader(b'123') as f:
            assert f.read(5) == b'123'
    
    def test_read_empty(self):
        with self._reader(b'123') as f:
            assert f.read(0) == b''
    
    def test_read_from_empty(self):
        with self._reader(b'') as f:
            assert f.read() == b''
    
    def test_seek(self):
        with self._reader(b'123') as f:
            f.seek(2)
            assert f.read(2) == b'3'
    
    def test_reseek(self):
        with self._reader(b'1234567') as f:
            f.seek(5)
            assert f.read(2) == b'67'
            f.seek(2)
            assert f.read(3) == b'345'
    
    def test_read_without_unrelated_part(self):
        d = {}
        with self._reader(b'1234', out = d) as f:
            d['bundle'].delete(1)
            f.seek(2)
            assert f.read() == b'34'
    
    def test_read_without_related_part(self):
        d = {}
        with self._reader(b'1234',out=d) as f:
            d['bundle'].delete(1)
            with self.assertRaises(Exception):
                f.read(1)
            d['bundle'].dump(b'12')
            assert f.read(3) == b'123'
    
    def test_after_close(self):
        f = self._reader(b'1234')
        f.close()
        with self.assertRaises(Exception):
            f.close()
        with self.assertRaises(Exception):
            f.read(0)
    
    def test_read_noise_tail(self):
        d = {}
        with self._reader(b'123', out=d) as f:
            d['bundle'].dump(2,b'34')
            assert f.read(1) == b'1'
            assert f.read(1) == b'2'
            assert f.read(2) == b'3'
    
    def _reader(self, data, part_size = 2, out = {}):
        b = bundle()
        fs = files(b)
        with writer(fs, part_size) as f:
            f.write(data)
        out['bundle'] = b
        return reader(fs, part_size)