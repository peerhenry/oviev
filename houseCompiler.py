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
  requiredKeys = ['HouseCode', 'BasicInformationV3', 'LanguagePackNLV4', 'MinMaxPriceV1']
  validLevel1 = jsonHasKeys(houseExtra, requiredKeys)
  if not validLevel1: return False
  return True

def tryCompileHouseData(house, houseExtra, regionsDic):
  validHouse = validateHouse(house)
  if not validHouse: return ''
  validHouseExtra = validateHouseExtra(houseExtra)
  if not validHouseExtra: return ''
  return compileHouseData(house, houseExtra, regionsDic)

def resolveRegion(regCode, regDic):
  if regCode in regDic:
    return regDic[regCode]
  else:
    print('Warning! region code not found: ' + regCode)
    return regCode

def compileHouseData(house, houseExtra, regionsDic):
  basics = houseExtra['BasicInformationV3']
  langData = houseExtra['LanguagePackNLV4']
  media = houseExtra['MediaV2']
  houseType = house['HouseType']
  city = langData['City']
  maxPersons = str(basics['MaxNumberOfPersons'])
  title = houseType+' huren in '+city+', max '+maxPersons+'personen'

  countryCode = basics['Country']
  country = resolveRegion(countryCode, regionsDic)
  regionCode = basics['Region']
  region = resolveRegion(regionCode, regionsDic)
  formattedLocation = city
  if 'SubCity' in langData and langData['SubCity']:
    formattedLocation = formattedLocation + ', ' + langData['SubCity']
  formattedLocation = formattedLocation + ', ' + region + ', ' + country

  meta = houseType+' huren voor '+maxPersons+'personen in '+formattedLocation
  compiled = { 'Title': title }
  compiled['Description'] = langData['Description']
  compiled['meta'] = meta
  # todo: get currency
  compiled['MinMaxPrice'] = houseExtra['MinMaxPriceV1'] # price, pricesuffix
  compiled['Area'] = basics['DimensionM2']
  compiled['Bathrooms'] = basics['NumberOfBathrooms']
  compiled['Bedrooms'] = basics['NumberOfBedrooms']
  compiled['CreationDate'] = basics['CreationDate']
  # ? landlord
  # ? agencies
  # ? agents
  # ? sliderimage
  compiled['Location'] = {
    'Address': {
      # missing street address
      'PostalCode': basics['ZipPostalCode'],
      'Country': country,
      'Region': region
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
  return compiled

def extractImageUrls(thing):
  urls = []
  contents = thing['TypeContents']
  for content in contents:
    firstVersion = content["Versions"][0]
    urls.append(firstVersion["URL"])
  return urls