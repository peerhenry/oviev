def compile(regRefList):
  dic = dict()
  counter = 0
  for el in regRefList:
    regions = el['Regions']
    countryCode = el['CountryCode']
    dutchCountryName = extractDutchName(el['CountryDescription'])
    dic[str(countryCode)] = dutchCountryName
    counter += 1
    # add regions
    for reg in regions:
      code = reg['RegionCode']
      langNames = reg['RegionDescription']
      dutchName = extractDutchName(langNames)
      dic[str(code)] = dutchName
      counter += 1
  print('compiled '+str(counter)+' regions')
  return dic

def extractDutchName(descriptionArray):
  for langName in descriptionArray:
    if langName['Language'] == 'NL':
      return langName['Description']