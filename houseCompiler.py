validLayoutItems = [
  '10400', # Zwembad
  '10358', # Tuin
  '10150', # Afwasmachine  
  '10040', # Open haard
  '10354', # Airconditioning
  '10255', # Wasmachine
  '10362', # BBQ  
  '10130', # Oven  
  '10140', # Magnetron  
  '10560', # Kinderstoel
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
  '6070', # Brede doorgang mindervaliden  
  '548'
]

validPropertyTypes = [
  '60', # Minder validen - Gecertificeerd
  '63', # Minder validen - Aangepaste douche
  '64', # Minder validen - Aangepast toilet  
  '65', # Minder validen - Lift
]

def jsonHasKeys(jsonData, keys):
  result = { 'isValid': True }
  for key in keys:
    if key not in jsonData:
      msg = 'invalid data, missing key: ' + key
      result['isValid'] = False
      result['message'] = msg
      return result
  return result

def validateHouse(house):
  requiredKeys = ['HouseCode', 'HouseType']
  return jsonHasKeys(house, requiredKeys)

def langDataIsValid(langData):
  requiredKeys = ['Description', 'City']
  result = jsonHasKeys(langData, requiredKeys)
  if not result['isValid']: return result
  if langData['City'] == None:
    result['isValid'] = None
    result['message'] = 'City in langdata is None'
  return result

def validateHouseExtra(houseExtra):
  requiredKeys = ['BasicInformationV3', 'LanguagePackNLV4', 'MinMaxPriceV1', 'PropertiesV1', 'LayoutExtendedV2']
  validResult = jsonHasKeys(houseExtra, requiredKeys)
  if not validResult['isValid']: return validResult
  validResult = langDataIsValid(houseExtra['LanguagePackNLV4'])
  return validResult

def validateHouseData(house, houseExtra):
  validHouseResult = validateHouse(house)
  if not validHouseResult['isValid']:
    return validHouseResult
  validHouseExtra = validateHouseExtra(houseExtra)
  if not validHouseExtra['isValid']:
    return validHouseExtra
  return { 'isValid': True }

def tryCompileHouseData(house, houseExtra, refDics):
  validResult = validateHouseData(house, houseExtra)
  if not validResult['isValid']:
    print('invalid data:', validResult['message'])
    return ''
  else: return compileHouseData(house, houseExtra, refDics)

def resolveRegion(regCode, regDic):
  if regCode in regDic:
    return regDic[regCode]
  else:
    print('Warning! region code not found: ' + regCode)
    return regCode

def compileHouseData(house, houseExtra, refDics):
  basics = houseExtra['BasicInformationV3']
  langData = houseExtra['LanguagePackNLV4']
  maxPersons = str(basics['MaxNumberOfPersons'])
  compiled_properties = compileProperties(houseExtra, refDics)
  compiledHousetype = compileHouseType(compiled_properties)
  location = extractLocation(langData, basics, refDics)
  compiled = { 'Title': formatTitle(compiledHousetype, location, maxPersons) }
  compiled['Description'] = langData['Description']
  compiled['Meta'] = formatMeta(compiledHousetype, maxPersons, location)
  compiled['HouseType'] = compiledHousetype
  compiled['MaxPersons'] = maxPersons
  compiled['SkiArea'] = house['SkiArea']
  compiled['HolidayPark'] = basics['HolidayPark']
  compiled['MinMaxPrice'] = houseExtra['MinMaxPriceV1'] # price, pricesuffix
  compiled['ExceedNumberOfBabies'] = basics['ExceedNumberOfBabies']
  compiled['NumberOfStars'] = basics['NumberOfStars']
  compiled['DimensionM2'] = basics['DimensionM2']
  compiled['Bathrooms'] = basics['NumberOfBathrooms']
  compiled['Bedrooms'] = basics['NumberOfBedrooms']
  compiled['Location'] = compileLocation(basics, location)
  compiled['PropertyId'] = house['HouseCode']
  compileImages(houseExtra, compiled)
  compiled_amenities = compileAmenities(house, houseExtra, refDics)
  compiled['Amenities'] = compiled_amenities
  compiled['Properties'] = compiled_properties
  return compiled

def extractLocation(langData, basics, refDics):
  countryCode = basics['Country']
  country = refDics.resolveRegion(countryCode)
  regionCode = basics['Region']
  region = refDics.resolveRegion(regionCode)
  city = langData['City']
  subcity = ''
  if 'SubCity' in langData and langData['SubCity']:
    subcity = langData['SubCity']
  return {
    'City': city,
    'Country': country,
    'Region': region,
    'SubCity': subcity
  }

def compileImages(houseExtra, compiled):
  media = houseExtra['MediaV2']
  for thing in media:
    if thing['Type'] == 'Photos':
      urls_1024 = extractImageUrls(thing, 1)
      images_1024 = ','.join(urls_1024)
      compiled['Images_1024x683'] = images_1024

      urls_750 = extractImageUrls(thing, 2)
      compiled['Images_750x500'] = ','.join(urls_750)

      urls_600 = extractImageUrls(thing, 3)
      compiled['Images_600x400'] = ','.join(urls_600)

      urls_330 = extractImageUrls(thing, 4)
      images_330 = ','.join(urls_330)
      compiled['Images_330x220'] = images_330

      compiled['Images'] = images_1024

def compileAmenities(house, houseExtra, refDics):
  amenities = extractAmenities(house, houseExtra, refDics)
  compiled_amenities = ','.join(amenities)
  return compiled_amenities

def formatTitle(compiledHousetype, location, maxPersons):
  title = ''
  if 'City' in location and location['City']:
    title = compiledHousetype + ' huren in ' + location['City'] + ', max ' + maxPersons + ' personen'
  else: 
    title = compiledHousetype + ' huren voor max ' + maxPersons + ' personen'
  return title

def formatMeta(compiledHousetype, maxPersons, location):
  formattedLocation = formatLocation(location)
  meta = compiledHousetype+' huren voor '+maxPersons+' personen in '+formattedLocation
  return meta

def formatLocation(location):
  formattedLocation = location['City']
  if location['SubCity']:
    formattedLocation = formattedLocation + ', ' + location['SubCity']
  formattedLocation = formattedLocation + ', ' + location['Region'] + ', ' + location['Country']
  return formattedLocation

def compileHouseType(compiled_properties):
  compiledHousetype = compiled_properties['Soort'][0] # just take the first entry in list of types
  return compiledHousetype

def compileLocation(basics, location):
  compiledLocation = {
    'Address': {
      # missing street address
      'PostalCode': basics['ZipPostalCode'],
      'Country': location['Country'],
      'Region': location['Region'],
      'City': location['City'],
      'Subcity': location['SubCity']
    },
    'Latitude': basics['WGS84Latitude'],
    'Longitude': basics['WGS84Longitude']
  }
  return compiledLocation

def compile_costs_on_site(langData):
  compiledCostsOnSite = []
  costsOnSite = langData['CostsOnSite']
  for amn in costsOnSite:
    compiledCostsOnSite.append(amn['Description']+' '+amn['Value'])
  return compiledCostsOnSite

def compileProperties(houseExtra, refDics):
  properties = houseExtra['PropertiesV1']
  compiled_properties = {}
  for entry in properties:
    typenr = entry['TypeNumber']
    pType = refDics.resolvePropertyType(typenr)
    contentList = []
    for contentCode in entry['TypeContents']:
      content = refDics.resolveProperty(contentCode)
      contentList.append(content)
    compiled_properties[pType] = contentList
  return compiled_properties

def extractAmenities(house, houseExtra, refDics):
  properties = houseExtra['PropertiesV1']
  layout = houseExtra['LayoutExtendedV2']
  amenities = []
  # add items from properties to amenities
  for entry in properties:
    typenr = entry['TypeNumber']
    if str(typenr) in validPropertyTypes:
      pType = refDics.resolvePropertyType(typenr)
      if(typenr >= 60):
        pType.replace("Minder validen", "Mindervaliden")
      if not pType in amenities:
        amenities.append(pType)
    for c in entry['TypeContents']:
      thing = refDics.resolveProperty(c)
      if str(c) in validProperties and not thing in amenities:
        amenities.append(thing)
  # add layout items to amenities
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
  # add other amenities
  if 'SkiArea' in house:
    amenities.append('In een skigebied')
  if 'Pets' in house:
    if house['Pets'] == 'no':
      amenities.append('Huisdieren niet toegestaan')
    else:
      amenities.append('Huisdieren toegestaan')
  return amenities

# todo: prompt user for photo size
def extractImageUrls(thing, variationIndex):
  urls = []
  contents = thing['TypeContents']
  limit = 10
  counter = 0
  for content in contents:
    firstVersion = content["Versions"][variationIndex]
    urls.append('http://'+firstVersion["URL"])
    counter += 1
    if(counter >= limit):
      break
  return urls
# version resolutions by variationIndex:
# 0 - 2048x1365
# 1 - 1024x683
# 2 - 750x500
# 3 - 600x400
# 4 - 330x220
  