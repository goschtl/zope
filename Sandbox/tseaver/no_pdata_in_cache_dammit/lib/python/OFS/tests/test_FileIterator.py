import unittest

class FileIteratorTests(unittest.TestCase):

    def _getTargetClass(self):
        from OFS.Image import FileIterator
        return FileIterator

    def _makeOne(self, fileobj, *args, **kw):
        return self._getTargetClass()(fileobj, *args, **kw)

    def _makeFile(self, id='test', title='', file='', chunks=()):
        from OFS.Image import File
        from OFS.Image import Pdata
        fileobj = File(id, title, file)
        jar = fileobj._p_jar = DummyConnection()
        if chunks:
            chunks = list(chunks)
            chunks.reverse()
            head = None
            for chunk in chunks: # build Pdata chain
                pdata = Pdata(chunk)
                pdata.next = head
                head = pdata
            fileobj.data = head
        return fileobj

    def test_class_conforms_to_Z2_IStreamIterator(self):
        from Interface.Verify import verifyClass
        from ZPublisher.Iterators import IStreamIterator
        verifyClass(IStreamIterator, self._getTargetClass())

    def test_instance_conforms_to_Z2_IStreamIterator(self):
        from Interface.Verify import verifyObject
        from ZPublisher.Iterators import IStreamIterator
        verifyObject(IStreamIterator, self._makeOne(self._makeFile()))

    def test___len___raises_NotImplementedErrlr(self):
        fileobj = self._makeFile()
        iterator = self._makeOne(fileobj)
        self.assertRaises(NotImplementedError, lambda: len(iterator))

    def test_iteration_over_empty_file(self):
        fileobj = self._makeFile()
        iterator = self._makeOne(fileobj)

        self.assertEqual(fileobj._p_jar._close_called, None)
        self.assertRaises(StopIteration, iterator.next)
        self.assertEqual(fileobj._p_jar._close_called, (False,))

    def test_iteration_over_file_with_string(self):
        ABC = 'ABC'
        fileobj = self._makeFile(file=ABC)
        iterator = self._makeOne(fileobj)

        chunk = iterator.next()
        self.assertEqual(chunk, ABC)

        self.assertEqual(fileobj._p_jar._close_called, None)
        self.assertRaises(StopIteration, iterator.next)
        self.assertEqual(fileobj._p_jar._close_called, (False,))

    def test_iteration_over_file_with_one_chunk(self):
        ABC = 'ABC'
        fileobj = self._makeFile(chunks=(ABC,))
        iterator = self._makeOne(fileobj)

        chunk = iterator.next()
        self.assertEqual(chunk, ABC)

        self.assertEqual(fileobj._p_jar._close_called, None)
        self.assertRaises(StopIteration, iterator.next)
        self.assertEqual(fileobj._p_jar._close_called, (False,))

    def test_iteration_over_file_with_one_chunk(self):
        CHUNKS = ('ABC', 'DEF', 'GHI', 'JKL')
        fileobj = self._makeFile(chunks=CHUNKS)
        iterator = self._makeOne(fileobj)

        for expected in CHUNKS:
            found = iterator.next()
            self.assertEqual(found, expected)

        self.assertEqual(fileobj._p_jar._close_called, None)
        self.assertRaises(StopIteration, iterator.next)
        self.assertEqual(fileobj._p_jar._close_called, (False,))

    def test___del___closes_targets_jar_not_as_primary(self):
        fileobj = self._makeFile()
        iterator = self._makeOne(fileobj)
        self.assertEqual(fileobj._p_jar._close_called, None)
        del iterator
        self.assertEqual(fileobj._p_jar._close_called, (False,))

class DummyConnection:

    _close_called = None

    def register(self, obj):
        pass

    def close(self, primary=True):
        self._close_called = (primary,)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FileIteratorTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
