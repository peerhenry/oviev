validLayoutItems = [
  '10400', # Zwembar
  '10358', #  Tuin
  '10150', # Afwasmachine  
  '10040', # Open haard
  '10354', # Airconditioning
  '10255', # Wasmachine
  '10362', # BBQ  
  '10130', # Oven  
  '10140', # Magnetron  
  '10560', # Kinderstoel	10560
  '10550', # Kinderbed
  '10570', # Kinderbox
  '3000', # Skiberging
  '10540', # Fietsen beschikbaar  
  '1170', # Jacuzzi / Bubbelbad  
  '1150', # Sauna  
  '1160', # Turks stoombad  
  '10235' # Zonnebank / solarium
]

validProperties = [
  '510', # Wifi
  '390', # Op vakantiepark  
  '370', # In de bergen  
  '394', # Aan de skipiste
  '360', # Landelijk    
  '504', # Roken toegestaan
  '502', # Niet roken
  '65', # Minder validen  - lift
  '64', # Aangepast toilet  
  '63', # Aangepaste douche  
  '6070', # Brede doorgang mindervaliden  
  '548'
]

validPropertyTypes = [
  '60' # Gecertificeerd voor mindervaliden  
]

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
  meta = houseType+' huren voor '+maxPersons+' personen in '+formattedLocation

  costsOnSite = langData['CostsOnSite']
  compiledCostsOnSite = []
  for amn in costsOnSite:
    compiledCostsOnSite.append(amn['Description']+' '+amn['Value'])
  
  amenities = []
  
  compiledPropertiesV1 = [] # todo: use refDics.properties
  for entry in properties:
    typenr = entry['TypeNumber']
    if str(typenr) in validPropertyTypes:
      pType = refDics.resolvePropertyType(typenr)
      if not pType in amenities:
        amenities.append(pType)
    for c in entry['TypeContents']:
      thing = refDics.resolveProperty(c)
      compiledPropertiesV1.append(thing)
      if str(c) in validProperties and not thing in amenities:
        amenities.append(thing)

  compiledLayoutExtendedV2 = [] # todo: use refDics.layoutItems & refDics.layoutDetails
  for entry in layout:
    itemKey = entry['Item']
    item = refDics.resolvelayoutItem(itemKey)
    thing = {
      'Item': item
    }
    if str(itemKey) in validLayoutItems and not item in amenities:
      amenities.append(item)
    if 'Details' in entry:
      thing['Details'] = []
      for detailKey in entry['Details']:
        detail = refDics.resolveLayoutDetail(detailKey)
        thing['Details'].append(detail)
    compiledLayoutExtendedV2.append(thing)
  
  if skiArea:
    amenities.append('In een skigebied')
  
  if 'Pets' in house:
    if house['Pets'] == 'no':
      amenities.append('Huisdieren niet toegestaan')
    else:
      amenities.append('Huisdieren toegestaan')

  compiled = { 'Title': title }
  compiled['Description'] = langData['Description']
  compiled['Meta'] = meta
  compiled['HouseType'] = houseType
  compiled['MaxPersons'] = maxPersons
  compiled['SkiArea'] = skiArea
  compiled['HolidayPark'] = holidayPark
  # todo: get currency
  compiled['MinMaxPrice'] = houseExtra['MinMaxPriceV1'] # price, pricesuffix
  compiled['ExceedNumberOfBabies'] = basics['ExceedNumberOfBabies']
  compiled['NumberOfStars'] = basics['NumberOfStars']
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

  for thing in media:
    if thing['Type'] == 'Photos':
      urls = extractImageUrls(thing)
      compiled['Images'] = urls
  
  # compiled['CostsOnSite'] = compiledCostsOnSite # debug
  # compiled['PropertiesV1'] = compiledPropertiesV1 # debug
  # compiled['LayoutExtendedV2'] = compiledLayoutExtendedV2 # debug
  compiled['Amenities'] = amenities

  return compiled

def extractImageUrls(thing):
  urls = []
  contents = thing['TypeContents']
  for content in contents:
    firstVersion = content["Versions"][0]
    urls.append(firstVersion["URL"])
  return urls
  