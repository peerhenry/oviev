import unittest
# import houseCompiler
from houseCompiler import *
import json

class HouseCompilerTests(unittest.TestCase):

  def test_jsonHasKeys_noKeys(self):
    data = {}
    data["key"] = "value"
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertFalse(result['isValid'])
  
  def test_jsonHasKeys_oneKey(self):
    data = {'a': 'value'}
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertFalse(result['isValid'])

  def test_jsonHasKeys_allKeys(self):
    data = {"a": "value_a", "b": "value_b"}
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertTrue(result['isValid'])
  
  def test_validateHouse_invalid(self):
    data = {"a": "value_a", "b": "value_b"}
    house = json.dumps(data)
    result = validateHouse(house)
    self.assertFalse(result['isValid'])
  
  def test_validateHouse_valid(self):
    data = {"HouseCode": "value_a", "HouseType": "value_b"}
    house = json.dumps(data)
    result = validateHouse(house)
    self.assertTrue(result['isValid'])