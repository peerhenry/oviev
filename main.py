import requests
import json
import sys
import os
import msvcrt as m
from leisure_partners_fetcher import LeisurePartnersFetcher as Fetcher
from ref_dics import RefDics
import houseCompiler

outDir = 'generated'
exampleDir = 'example'
referenceDir = 'reference'
packageDir = 'packaged'

allItems = [
  'BasicInformationV3',
  'MediaV2',
  'LanguagePackNLV4', # contains CostsOnSite
  # 'LanguagePackFRV4',
  # 'LanguagePackDEV4',
  # 'LanguagePackENV4',
  # 'LanguagePackITV4',
  # 'LanguagePackESV4',
  # 'LanguagePackPLV4',
  'MinMaxPriceV1',
  'AvailabilityPeriodV1',
  'PropertiesV1', # contains references to ReferencePropertiesV1
  'CostsOnSiteV1',
  'LayoutExtendedV2', # contains references to ReferenceLayoutItemsV1 and ReferenceLayoutDetailsV1
  'DistancesV2',
  'DistancesV1',
]

distilledItems = ['BasicInformationV3', 'LanguagePackNLV4', 'MinMaxPriceV1', 'MediaV2', 'PropertiesV1', 'LayoutExtendedV2']

counter = 0
compileCounter = 0
packageCounter = 1

def main():
  intro()
  print('creating output directories...')
  checkCreateOutDirs()
  print('fetching list of houses...')
  fetcher = Fetcher()
  listOfHouses = fetcher.fetchListOfHouses()
  writeHousCodes(listOfHouses)
  count = str(len(listOfHouses))
  print('Succesfully retrieved ' + count + ' results!')
  print('*')
  refDics = RefDics(fetcher)
  refDics.writeDicsToFiles(outDir + '/' + referenceDir)
  house1 = listOfHouses[1]
  generateDataExamples(fetcher, house1, refDics)
  print('*')
  print('Ready to start data fetch for each house...')
  print('Note that downloading all data at once can take up to 2 hours...')
  setting = promptForSettings()
  print('Starting data ofetch for each house...')
  handleListOfHouses(fetcher, listOfHouses, refDics, setting)
  print('*')
  outro()

def intro():
  print()
  print("############ Leisure Partners Package Maker v1.0 ############")
  print("This process will retrieve data from www.leisure-partners.net and assemble one or more files that are suitable for WP All Import")
  print()

# vvvvvvvvvvvvvvvvvvvv PROMPT vvvvvvvvvvvvvvvvvvvv

def promptForSettings():
  settings = dict()
  settings['downloadLimit'] = -1
  limitDownloadMessage = 'Would you like to limit the amount of houses to download? (y/n)'
  limitDownload = promtForBool(limitDownloadMessage)
  if limitDownload:
    settings['downloadLimit'] = promtForNumber('howmany entries would you like to download?')
  promt1 = 'What is the maximum amount of entries you want in a package? (recommended: 200)'
  settings['packageLimit'] = promtForNumber(promt1)
  customStart = promtForBool('Would you like to set a custom starting index (for example 10 to start packaging at the tenth entry)? (y/n)')
  if customStart:
    settings['offset'] = promtForNumber('Please enter the index where you would like the packaging to begin')
  return settings

def promtForBool(prompt):
  print(prompt)
  limit = input()
  valid = limit == 'y' or limit == 'n'
  if not valid:
    print('you must enter y or n')
    return promtForBool(prompt)
  else:
    return limit == 'y'

def promtForNumber(prompt):
  print(prompt)
  limit = input()
  valid = limit.isdigit()
  if not valid:
    print('you must specify a number')
    return promtForNumber(prompt)
  else:
    return int(limit)

def promptForString(prompt):
  print(prompt)
  return input()

# ^^^^^^^^^^^^^^^^^^^^ PROMPT ^^^^^^^^^^^^^^^^^^^^

def writeHousCodes(listOfHouses):
  codes = list(map(lambda house: house['HouseCode'], listOfHouses))
  # enumerated_codes = [enumerate(codes)]
  writeToJson(outDir + '/' + 'list_of_house_codes', codes)

def handleListOfHouses(fetcher, listOfHouses, refDics, settings):
  packageLimit = settings['packageLimit']
  downloadLimit = settings['downloadLimit']
  offset = determineOffset(settings, listOfHouses)
  limit = len(listOfHouses) - offset
  if downloadLimit >= 1 and downloadLimit < limit:
    limit = downloadLimit
  while counter < limit:
    handleListOfHousesInRange(fetcher, listOfHouses, refDics, packageLimit, limit, offset)

def determineOffset(settings, listOfHouses):
  if 'offset' in settings:
    offset = settings['offset']
    if offset >= len(listOfHouses):
      print('Error: the offset '+offset+' must be less than the length of houses '+len(listOfHouses))
    return offset
  else: return 0

def houseHasValidBrand(house):
  brands = house['Brands']
  for brand in brands:
    if brand['Brand'] == 'BV':
      return True
  return False

def houseIsValid(house):
  houseType = house['HouseType']
  if houseType == 'Boot' or houseType == 'Woonboot' or houseType == 'Tent lodge':
    return False
  return houseHasValidBrand(house)

def handleListOfHousesInRange(fetcher, listOfHouses, refDics, packageLimit, limit, offset):
  global counter
  global compileCounter
  global packageCounter
  compiledHouses = []
  for n in range(packageLimit):
    house = listOfHouses[offset + counter]
    counter += 1
    valid = houseIsValid(house)
    if valid:
      distilledData = distillHouseData(fetcher, house)
      compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, refDics)
      if compileHouseData:
        compiledHouses.append(compileHouseData)
        compileCounter += 1
    if compileCounter >= limit: break
    printProgress(counter, limit)
  serializable = {
    'Houses': compiledHouses
  }
  writeDataPackage('data-package-' + str(packageCounter), serializable)
  packageCounter += 1

def checkCreateOutDirs():
  if not os.path.exists(outDir):
    os.makedirs(outDir)
  if not os.path.exists(outDir + '/' + exampleDir):
    os.makedirs(outDir + '/' + exampleDir)
  if not os.path.exists(outDir + '/' + packageDir):
    os.makedirs(outDir + '/' + packageDir)
  if not os.path.exists(outDir + '/' + referenceDir):
    os.makedirs(outDir + '/' + referenceDir)

def generateDataExamples(fetcher, house, refDics):
  writeExampleData('1. data-house-list-item', house)
  code = house['HouseCode']
  allDetails = fetcher.fetchHouseDetails([ code ], allItems)
  writeExampleData('2. data-house-all-details', allDetails)
  distilledData = distillHouseData(fetcher, house)
  del distilledData['LanguagePackNLV4']['GuestBook']
  writeExampleData('3. data-house-distilled', distilledData)
  compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, refDics)
  writeExampleData('4. data-house-compiled', compileHouseData)

def distillHouseData(fetcher, house):
  code = house['HouseCode']
  distilled = fetcher.fetchHouseDetails([ code ], distilledItems )
  return distilled

def writeExampleData(fileName, jsonObject):
  filePath = outDir + '/' + exampleDir + '/' + fileName
  writeToJson(filePath, jsonObject)

def writeReferenceData(fileName, jsonObject):
  filePath = outDir + '/' + referenceDir + '/' + fileName
  writeToJson(filePath, jsonObject)

def writeDataPackage(fileName, jsonObject):
  filePath = outDir + '/' + packageDir + '/' + fileName
  writeToJson(filePath, jsonObject)

def writeToJson(fileName, jsonObject):
  fileNameExt = fileName + '.json'
  with open(fileNameExt, 'w') as outfile:
    json.dump(jsonObject, outfile, indent=2)
  print('exported ' + fileNameExt)

def outro():
  print()
  print("Finished!")
  print("Press any key to close")
  print()
  m.getch()

def printProgress(counter, count):
  percent = round((float(counter) / count)*100)
  line = str(counter) + '/' + str(count) + ' ' + str(percent) + '%'
  print(line, end='\r')

main()