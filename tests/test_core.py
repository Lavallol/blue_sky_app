from django.test import TestCase
from core.models import TimeStampedModel

class TimeStampedModelTest(TestCase):
    def test_model_has_timestamps(self):
        obj = TimeStampedModel()
        self.assertTrue(hasattr(obj, 'created'))
        self.assertTrue(hasattr(obj, 'updated'))
