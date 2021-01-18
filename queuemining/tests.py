from django.test import TestCase
from django.test import Client
from .models import Data
import os
import sys
from shutil import copyfile
import ntpath
# Create your tests here.


class InputTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        sys.stderr.write(repr(os.getcwd()) + '\n')
        os.chdir('media/documents')
        path = os.getcwd()
        self.file_root = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        copyfile(self.path_leaf(self.file_root), '../documentstest/test.xes')
        os.chdir('../documentstest/')
        self.new_file = "test.xes"
        sys.stderr.write(repr(self.new_file) + '\n')


    def path_leaf(self,path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)


    def test_runInputTest(self):
        with open(self.new_file) as fd:
            self.c.post('/queuemining/', {'document': fd, 'offdays': ["0"], 'day_start': 2, 'day_end': 20,
                                          'timeframe': 2, 'unit': "D"})
            data = Data.objects.filter(document='documents/test.xes')
        os.remove(self.new_file)
        self.assertEqual(len(data), 1)
