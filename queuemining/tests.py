from django.test import TestCase
from django.test import Client
from .models import Data
import os
import sys
from shutil import copyfile
import ntpath
# Create your tests here.


class UploadTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        sys.stderr.write(repr(os.getcwd()) + '\n')
        os.chdir('media/documents')
        path = os.getcwd()
        self.file_root = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        copyfile(self.path_leaf(self.file_root), '../documentstest/test.xes')
        os.chdir('../documentstest/')
        self.new_file = os.path.realpath('test.xes')
        sys.stderr.write(repr(self.new_file) + '\n')

    def path_leaf(self,path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def test_runUploadTest(self):
        with open(self.new_file) as fd:
            self.c.post('/queuemining/', {'document': fd, 'unit': "D", 'timeframe': 2})
            data = Data.objects.filter(document = 'documents/test.xes').filter(unit = 'D', timeframe = 2)
           # data = data.objects.filter(unit = 'D', timeframe = 2)
            sys.stderr.write(repr(data) + '\n')
        os.remove(self.new_file)
        os.remove('../documents/test.xes')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].unit, 'D')
        self.assertEqual(data[0].timeframe, 2)
