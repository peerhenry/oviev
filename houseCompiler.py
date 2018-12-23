def jsonHasKeys(jsonData, keys):
  for key in keys:
    if key not in jsonData:
      print('invalid data, missing key: ', key)
      return False
  return True

def validateHouse(house):
  requiredKeys = ['HouseCode', 'HouseType']
  return jsonHasKeys(house, requiredKeys)

def validateHouseExtra(houseExtra):
  requiredKeys = ['HouseCode', 'BasicInformationV3', 'LanguagePackNLV4', 'MinMaxPriceV1', 'PropertiesV1', 'LayoutExtendedV2']
  validLevel1 = jsonHasKeys(houseExtra, requiredKeys)
  if not validLevel1: return False
  return True

def tryCompileHouseData(house, houseExtra, refDics):
  validHouse = validateHouse(house)
  if not validHouse: return ''
  validHouseExtra = validateHouseExtra(houseExtra)
  if not validHouseExtra: return ''
  return compileHouseData(house, houseExtra, refDics)

def resolveRegion(regCode, regDic):
  if regCode in regDic:
    return regDic[regCode]
  else:
    print('Warning! region code not found: ' + regCode)
    return regCode

def compileHouseData(house, houseExtra, refDics):
  basics = houseExtra['BasicInformationV3']
  langData = houseExtra['LanguagePackNLV4']
  media = houseExtra['MediaV2']
  properties = houseExtra['PropertiesV1']
  layout = houseExtra['LayoutExtendedV2']

  houseType = house['HouseType']
  skiArea = house['SkiArea']
  city = langData['City']
  subcity = ''
  maxPersons = str(basics['MaxNumberOfPersons'])
  title = houseType+' huren in '+city+', max '+maxPersons+' personen'
  holidayPark = basics['HolidayPark']
  countryCode = basics['Country']
  country = refDics.resolveRegion(countryCode)
  regionCode = basics['Region']
  region = refDics.resolveRegion(regionCode)
  formattedLocation = city
  if 'SubCity' in langData and langData['SubCity']:
    subcity = langData['SubCity']
    formattedLocation = formattedLocation + ', ' + langData['SubCity']
  formattedLocation = formattedLocation + ', ' + region + ', ' + country

  costsOnSite = langData['CostsOnSite'] # features, amenities & more
  compiledCostsOnSite = []
  for amn in costsOnSite:
    compiledCostsOnSite.append(amn['Description']+' '+amn['Value'])
  
  compiledPropertiesV1 = [] # todo: use refDics.properties
  for prop in properties:
    thing = {
      
    }
    compiledPropertiesV1.append(thing)

  compiledLayoutExtendedV2 = [] # todo: use refDics.layoutItems & refDics.layoutDetails

  meta = houseType+' huren voor '+maxPersons+' personen in '+formattedLocation
  compiled = { 'Title': title }
  compiled['Description'] = langData['Description']
  compiled['Meta'] = meta
  compiled['HouseType'] = houseType
  compiled['MaxPersons'] = maxPersons
  compiled['SkiArea'] = skiArea
  compiled['HolidayPark'] = holidayPark
  # todo: get currency
  compiled['MinMaxPrice'] = houseExtra['MinMaxPriceV1'] # price, pricesuffix
  compiled['DimensionM2'] = basics['DimensionM2']
  compiled['Bathrooms'] = basics['NumberOfBathrooms']
  compiled['Bedrooms'] = basics['NumberOfBedrooms']
  # compiled['CreationDate'] = basics['CreationDate'] # removed per request

  # ? landlord
  # ? agencies
  # ? agents
  # ? sliderimage

  compiled['Location'] = {
    'Address': {
      # missing street address
      'PostalCode': basics['ZipPostalCode'],
      'Country': country,
      'Region': region,
      'City': city,
      'Subcity': subcity
    },
    'Latitude': basics['WGS84Longitude'],
    'Longitude': basics['WGS84Latitude']
  }
  compiled['PropertyId'] = house['HouseCode']
  # ? optional title
  # ? custom text instead of price
  # locations
  # ? amenities

  for thing in media:
    if thing['Type'] == 'Photos':
      urls = extractImageUrls(thing)
      compiled['Images'] = urls
  
  compiled['CostsOnSite'] = compiledCostsOnSite
  compiled['PropertiesV1'] = compiledPropertiesV1
  compiled['LayoutExtendedV2'] = compiledLayoutExtendedV2

  return compiled

def extractImageUrls(thing):
  urls = []
  contents = thing['TypeContents']
  for content in contents:
    firstVersion = content["Versions"][0]
    urls.append(firstVersion["URL"])
  return urls
  