import unittest
# import houseCompiler
# from houseCompiler import *
from houseCompiler import jsonHasKeys, validateHouse, compileHouseData
import json

class MockRefDics:
  def resolveRegion(self, number):
    if number == 'AD': return 'Andorra'
    if number == 'TIR': return 'Tirol'
    return 'mockregion'
  def resolvePropertyType(self, number):
    if (number == 10): return 'Soort'
    return 'mockPropertyType'
  def resolveProperty(self, number):
    if number == 20: return 'Kasteel'
    if number == 30: return 'Cottage'
    return 'mockProperty'

class HouseCompilerIntegrationTests(unittest.TestCase):
  
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
        'Country': 'AD',
        'Region': 'TIR',
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

  def assertEqualKeys(self, left, right, key):
    self.assertEqual(left[key], right[key])

  def test_compileHouseData_success(self):
    # Arrange
    (house, houseExtra, refDics) = self.getMinimalDataForCompiler()
    # Act
    compiled = compileHouseData(house, houseExtra, refDics)
    # Assert
    basics = houseExtra['BasicInformationV3'];
    langData = houseExtra['LanguagePackNLV4']
    expectedMaxPersons = str(basics['MaxNumberOfPersons']);
    expectedTitle = 'Kasteel huren in ' + houseExtra['LanguagePackNLV4']['City'] +  ', max ' + expectedMaxPersons + ' personen'
    country = refDics.resolveRegion(basics['Country'])
    region = refDics.resolveRegion(basics['Region'])
    formattedLocation = langData['City'] + ', ' + region + ', ' + country
    expectedMeta = 'Kasteel huren voor ' + expectedMaxPersons + ' personen in ' + formattedLocation
    self.assertEqual(expectedTitle, compiled['Title'])
    self.assertEqualKeys(langData, compiled, 'Description')
    self.assertEqual(expectedMeta, compiled['Meta'])
    self.assertEqual('Kasteel', compiled['HouseType'])
    self.assertEqual(expectedMaxPersons, compiled['MaxPersons'])
    self.assertEqualKeys(house, compiled, 'SkiArea')
    self.assertEqualKeys(basics, compiled, 'HolidayPark')
    self.assertEqual(houseExtra['MinMaxPriceV1'], compiled['MinMaxPrice'])
    self.assertEqualKeys(basics, compiled, 'ExceedNumberOfBabies')
    self.assertEqualKeys(basics, compiled, 'NumberOfStars')
    self.assertEqualKeys(basics, compiled, 'DimensionM2')
    self.assertEqual(basics['NumberOfBathrooms'], compiled['Bathrooms'])
    self.assertEqual(basics['NumberOfBedrooms'], compiled['Bedrooms'])

    expectedLocation = {
      'Address': {
        'City': langData['City'],
        'Country': country,
        'PostalCode': basics['ZipPostalCode'],
        'Region': region,
        'Subcity': ''
      },
      'Latitude': '33',
      'Longitude': '55'
    }
    self.assertEqual(expectedLocation, compiled['Location'])
    # location
    self.assertEqual(house['HouseCode'], compiled['PropertyId'])
    # media
    self.assertEqual('In een skigebied', compiled['Amenities'])
    self.assertEqual({ 'Soort': ['Kasteel', 'Cottage'] }, compiled['Properties'])

