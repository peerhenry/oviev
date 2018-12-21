import requests
import json
import sys
import msvcrt as m
import houseCompiler
import regionCompiler

allItems = [
  'BasicInformationV3',
  'MediaV2',
  'LanguagePackNLV4',
  # 'LanguagePackFRV4',
  # 'LanguagePackDEV4',
  # 'LanguagePackENV4',
  # 'LanguagePackITV4',
  # 'LanguagePackESV4',
  # 'LanguagePackPLV4',
  'MinMaxPriceV1',
  'AvailabilityPeriodV1',
  'PropertiesV1',
  'CostsOnSiteV1',
  'LayoutExtendedV2',
  'DistancesV2',
  'DistancesV1',
]

distilledItems = ['BasicInformationV3', 'LanguagePackNLV4', 'MinMaxPriceV1', 'MediaV2']

loginParams = {
  'WebpartnerCode': '?',
  'WebpartnerPassword': '?'
}

counter = 0
packageCounter = 1

def main():
  intro()
  print('fetching list of houses...')
  listOfHouses = fetchListOfHouses()
  count = str(len(listOfHouses))
  print('Succesfully retrieved ' + count + ' results!')
  print('*')
  refRegions = fetchReferenceRegions()
  regionsDic = regionCompiler.compileRegions(refRegions)
  house0 = listOfHouses[0]
  generateDataRefs(house0, regionsDic)
  print('*')
  print('Ready to start data fetch for each house...')

  print('Note that downloading all data at once can take up to 2 hours...')
  setting = promptForSettings()
  packageLimit = setting['packageLimit']
  downloadLimit = setting['downloadLimit']

  print('Starting data fetch for each house...')
  handleListOfHouses(listOfHouses, regionsDic, packageLimit, downloadLimit)
  print('*')
  outro()

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

def intro():
  print()
  print("############ Leisure Partners Package Maker v1.0 ############")
  print("This process will retrieve data from www.leisure-partners.net and assemble one or more files that are suitable for WP All Import")
  print()

def createRpc(method, params):
  output = {
    'jsonrpc': '2.0',
    'method': method,
    'params': params,
    'id': 22298
  }
  return output

def httpPost(url, method, params):
  jsonPayload = createRpc(method, params)
  payload = json.dumps(jsonPayload)
  headers = {
    'Content-Type': "application/json",
    'cache-control': "no-cache",
  }
  response = requests.request("POST", url, data=payload, headers=headers)
  return response

def callLeisurePartners(method, params):
  url = 'https://' + method.lower() + '.jsonrpc-partner.net/cgi/lars/jsonrpc-partner/jsonrpc.htm'
  return httpPost(url, method, params)

def handleStatus(name, status):
  if status != 200 :
    print('http error during ' + name + ', status: ' + str(status))
    print('Press any key to exit...')
    m.getch()
    sys.exit(0)

def fetchListOfHouses():
  method = 'ListOfHousesV1'
  response = callLeisurePartners(method, loginParams)
  handleStatus(method, response.status_code)
  jsonResult = json.loads(response.text)
  resultList = jsonResult["result"]
  return resultList

def handleListOfHouses(listOfHouses, regionsDic, packageLimit, downloadLimit):
  count = len(listOfHouses)
  if downloadLimit >= 1:
    count = downloadLimit
  while counter < count:
    handleListOfHousesInRange(listOfHouses, regionsDic, packageLimit, count)

def handleListOfHousesInRange(listOfHouses, regionsDic, packageLimit, count):
  global counter
  global packageCounter
  compiledHouses = []
  for n in range(packageLimit):
    house = listOfHouses[counter]
    distilledData = distillHouseData(house)
    compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, regionsDic)
    compiledHouses.append(compileHouseData)
    counter += 1
    if counter >= count: break
    printProgress(counter, count)
  serializable = {
    'Houses': compiledHouses
  }
  writeToJson('data-package-' + str(packageCounter), serializable)
  packageCounter += 1
  

def fetchReferenceRegions():
  method = 'ReferenceRegionsV1'
  response = callLeisurePartners(method, loginParams)
  handleStatus(method, response.status_code)
  jsonResult = json.loads(response.text)
  resultList = jsonResult["result"]
  return resultList

def generateDataRefs(house, regionsDic):
  writeToJson('1. data-house-list-item', house)
  code = house['HouseCode']
  allDetails = fetchHouseDetails([ code ], allItems)
  writeToJson('2. data-house-all-details', allDetails)
  distilledData = distillHouseData(house)
  del distilledData['LanguagePackNLV4']['GuestBook']
  writeToJson('3. data-house-distilled', distilledData)
  compileHouseData = houseCompiler.tryCompileHouseData(house, distilledData, regionsDic)
  writeToJson('4. data-house-compiled', compileHouseData)

def distillHouseData(house):
  code = house['HouseCode']
  distilled = fetchHouseDetails([ code ], distilledItems )
  return distilled

def fetchHouseDetails(codes, items):
  params = {
    'WebpartnerCode': 'susanvannoort',
    'WebpartnerPassword': '@belvilla11', # old pw: '@belvilla11', new pw: '5ofd3r'
    'HouseCodes': codes,
    'Items': items
  }
  response = callLeisurePartners('DataOfHousesV1', params)
  status = response.status_code
  if status != 200:
    print('http error during fetchHouseDetails, status: ' + str(status))
    sys.exit(0)
  jsonResult = json.loads(response.text)
  result = jsonResult["result"]
  return result[0]

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