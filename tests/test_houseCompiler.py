import unittest
# import houseCompiler
# from houseCompiler import *
from houseCompiler import jsonHasKeys, validateHouse, compileHouseData
import json

class MockRefDics:
  def resolveRegion(self, number):
    return 'mockregion'
  def resolvePropertyType(self, number):
    if (number == 10): return 'Soort'
    return 'mockPropertyType'
  def resolveProperty(self, number):
    if number == 20: return 'Kasteel'
    if number == 30: return 'Cottage'
    return 'mockProperty'

class HouseCompilerTests(unittest.TestCase):

  def test_jsonHasKeys_noKeys(self):
    data = {}
    data["key"] = "value"
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertFalse(False)
  
  def test_jsonHasKeys_oneKey(self):
    data = {}
    data["key"] = "value"
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertFalse(False)

  def test_jsonHasKeys_allKeys(self):
    data = {"a": "value_a", "b": "value_b"}
    json_data = json.dumps(data)
    result = jsonHasKeys(json_data, ['a', 'b'])
    self.assertTrue(result)
  
  def test_validateHouse_invalid(self):
    data = {"a": "value_a", "b": "value_b"}
    house = json.dumps(data)
    result = validateHouse(house)
    self.assertFalse(result)
  
  def test_validateHouse_valid(self):
    data = {"HouseCode": "value_a", "HouseType": "value_b"}
    house = json.dumps(data)
    result = validateHouse(house)
    self.assertTrue(result)
  
  def test_sanity(self):
    empty = {}
    emptytwo = {}
    self.assertEqual(empty, emptytwo)
  
  def getMinimalDataForCompiler(self):
    house = {
      'HouseType': 'Pietje',
      'SkiArea': 'nah',
      'HouseCode': '1234'
    }
    houseExtra = {
      'BasicInformationV3': { # basics
        'MaxNumberOfPersons': 5,
        'HolidayPark': 'dummy',
        'Country': 'NL',
        'Region': 'Limbua',
        'ExceedNumberOfBabies' : 2,
        'NumberOfStars': 4,
        'DimensionM2': 200,
        'NumberOfBathrooms': 2,
        'NumberOfBedrooms': 1,
        'ZipPostalCode': '1234ab',
        'WGS84Latitude': '33',
        'WGS84Longitude': '55',
      },
      'LanguagePackNLV4': { # langData
        'City': 'NYX',
        'CostsOnSite': [],
        'Description': 'Pietje'
      },
      'MediaV2': [],
      'PropertiesV1': [{
        'TypeNumber': 10, # Soort
        'TypeContents': [20, 30] # Kasteel, Cottage
      }], # properties
      'LayoutExtendedV2': [],
      'MinMaxPriceV1': 'dummy'
    }
    refDics = MockRefDics()
    return (house, houseExtra, refDics)

  def assertEqualKeys(self, basics, compiled, key):
    self.assertEqual(basics[key], compiled[key])

  def test_compileHouseData_success(self):
    (house, houseExtra, refDics) = self.getMinimalDataForCompiler()
    compiled = compileHouseData(house, houseExtra, refDics)
    empty = {}
    basics = houseExtra['BasicInformationV3'];
    expectedTitle = 'Kasteel huren in ' + houseExtra['LanguagePackNLV4']['City'] +  ', max ' + str(basics['MaxNumberOfPersons']) + ' personen'
    self.assertEqual(expectedTitle, compiled['Title'])
    self.assertEqual(houseExtra['MinMaxPriceV1'], compiled['MinMaxPrice'])
    self.assertEqualKeys(basics, compiled, 'ExceedNumberOfBabies')
    self.assertEqualKeys(basics, compiled, 'NumberOfStars')
    self.assertEqualKeys(basics, compiled, 'DimensionM2')
    self.assertEqual(basics['NumberOfBathrooms'], compiled['Bathrooms'])
    self.assertEqual(basics['NumberOfBedrooms'], compiled['Bedrooms'])
  


