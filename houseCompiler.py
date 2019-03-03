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
  
  compiled_properties = {}
  for entry in properties:
    typenr = entry['TypeNumber']
    pType = refDics.resolvePropertyType(typenr)
    contentList = []
    for contentCode in entry['TypeContents']:
      content = refDics.resolveProperty(contentCode)
      contentList.append(content)
    compiled_properties[pType] = contentList
  
  amenities = extractAmenities(house, houseExtra, refDics)

  compiledHousetype = compiled_properties['Soort'][0] # just take the first entry in list of types
  title = compiledHousetype +' huren in '+city+', max '+maxPersons+' personen'

  compiled = { 'Title': title }
  compiled['Description'] = langData['Description']
  compiled['Meta'] = meta
  # compiled['HouseType'] = houseType # this is english
  compiled['HouseType'] = compiledHousetype
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
    'Latitude': basics['WGS84Latitude'],
    'Longitude': basics['WGS84Longitude']
  }
  compiled['PropertyId'] = house['HouseCode']
  # ? optional title
  # ? custom text instead of price
  # locations

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
  
  # compiled['CostsOnSite'] = compiledCostsOnSite # debug
  # compiled['PropertiesV1'] = compiledPropertiesV1 # debug
  # compiled['LayoutExtendedV2'] = compiledLayoutExtendedV2 # debug
  compiled['Amenities'] = ','.join(amenities)

  compiled['Properties'] = compiled_properties

  return compiled

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
  