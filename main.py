import requests
import json
import sys
import msvcrt as m
from leisure_partners_fetcher import LeisurePartnersFetcher as Fetcher
from ref_dics import RefDics
import houseCompiler

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
  print('fetching list of houses...')
  fetcher = Fetcher()
  listOfHouses = fetcher.fetchListOfHouses()
  count = str(len(listOfHouses))
  print('Succesfully retrieved ' + count + ' results!')
  print('*')
  refDics = RefDics(fetcher)
  house1 = listOfHouses[1]
  generateDataExamples(fetcher, house1, refDics)
  print('*')
  print('Ready to start data ofetch for each house...')
  print('Note that downloading all data at once can take up to 2 hours...')
  setting = promptForSettings()
  packageLimit = setting['packageLimit']
  downloadLimit = setting['downloadLimit']
  print('Starting data ofetch for each house...')
  handleListOfHouses(fetcher, listOfHouses, refDics, packageLimit, downloadLimit)
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
  return settings

def promtForBool(prompt):
  print(prompt)
  limit = input()
  valid = limit == 'y' or limit == 'n'
  if not valid:
    print('you must enter y or n')
    return promtForNumber(prompt)
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

# ^^^^^^^^^^^^^^^^^^^^ PROMPT ^^^^^^^^^^^^^^^^^^^^

def handleListOfHouses(fetcher, listOfHouses, refDics, packageLimit, downloadLimit):
  count = len(listOfHouses)
  if downloadLimit >= 1:
    count = downloadLimit
  while counter < count:
    handleListOfHousesInRange(fetcher, listOfHouses, refDics, packageLimit, count)

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

def handleListOfHousesInRange(fetcher, listOfHouses, refDics, packageLimit, count):
  global counter
  global compileCounter
  global packageCounter
  compiledHouses = []
  for n in range(packageLimit):
    house = listOfHouses[counter]
    counter += 1
    valid = houseIsValid(house)
    if valid:
      distilledData = distillHouseData(fetcher, house)
      compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, refDics)
      compiledHouses.append(compileHouseData)
      compileCounter += 1
    if compileCounter >= count: break
    printProgress(counter, count)
  serializable = {
    'Houses': compiledHouses
  }
  writeToJson('data-package-' + str(packageCounter), serializable)
  packageCounter += 1

def generateDataExamples(fetcher, house, refDics):
  writeToJson('1. data-house-list-item', house)
  code = house['HouseCode']
  allDetails = fetcher.fetchHouseDetails([ code ], allItems)
  writeToJson('2. data-house-all-details', allDetails)
  distilledData = distillHouseData(fetcher, house)
  del distilledData['LanguagePackNLV4']['GuestBook']
  writeToJson('3. data-house-distilled', distilledData)
  compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, refDics)
  writeToJson('4. data-house-compiled', compileHouseData)

def distillHouseData(fetcher, house):
  code = house['HouseCode']
  distilled = fetcher.fetchHouseDetails([ code ], distilledItems )
  return distilled

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
  line = str(counter)+'/'+str(count) + ' ' + str(percent) + '%'
  print(line, end='\r')

main()