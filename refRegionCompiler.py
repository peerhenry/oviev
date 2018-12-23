def compile(regRefList):
  dic = dict()
  for el in regRefList:
    regions = el['Regions']
    countryCode = el['CountryCode']
    dutchCountryName = extractDutchName(el['CountryDescription'])
    dic[countryCode] = dutchCountryName
    # add regions
    for reg in regions:
      code = reg['RegionCode']
      langNames = reg['RegionDescription']
      dutchName = extractDutchName(langNames)
      dic[code] = dutchName
  return dic

def extractDutchName(descriptionArray):
  for langName in descriptionArray:
    if langName['Language'] == 'NL':
      return langName['Description']