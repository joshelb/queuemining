from django.test import TestCase
from django.test import Client
from .models import Document
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
            self.c.post('/queuemining/',{'document': fd})
            document = Document.objects.filter(document = 'documents/test.xes')
            sys.stderr.write(repr(document) + '\n')
        os.remove(self.new_file)
        os.remove('../documents/test.xes')
        self.assertEqual(len(document),1)




