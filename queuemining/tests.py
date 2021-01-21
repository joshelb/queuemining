from django.test import TestCase
from django.test import Client
from .models import Data,TimeStep
from datetime import timezone
import os
import sys
from shutil import copyfile
import ntpath
# Create your tests here.


class InputTestCase(TestCase):
    def setUp(self):
        data = Data.objects.create(id = 1, document = None)
        object = TimeStep.objects.create(unit = "H")
        data.timestep.add(object)
    def testdataobject(self):
        a = Data.objects.get(id = 1).timestep.all()
        self.assertEqual(a[0].unit, "H")