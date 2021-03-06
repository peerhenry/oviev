import json
import refRegionCompiler
import refPropertyTypesCompiler
import refPropertiesCompiler
import refLayoutItemsCompiler
import refLayoutDetailsCompiler

class RefDics:
  def __init__(self, fetcher):
    self.fetcher = fetcher
    self.regions = self.generateRefRegions()
    self.propertyTypes = self.generateRefPropertyTypes()
    self.properties = self.generateRefProperties()
    self.layoutItems = self.generateRefLayoutItems()
    self.layoutDetails = self.generateRefLayoutDetails()
  
  def writeDicsToFiles(self, path):
    self.writeDicToFile(self.regions, path,  'regions')
    self.writeDicToFile(self.properties, path, 'properties')
    self.writeDicToFile(self.propertyTypes, path, 'propertyTypes')
    self.writeDicToFile(self.layoutItems, path, 'layoutItems')
    self.writeDicToFile(self.layoutDetails, path, 'layoutDetails')

  def writeDicToFile(self, dic, path, name):
    with open(path + '/ref_'+name+'.txt', 'w') as file:
      file.write(json.dumps(dic, indent=4))
  
  def generateRefRegions(self):
    result = self.fetcher.simpleFetchMethod('ReferenceRegionsV1')
    return refRegionCompiler.compile(result)
  
  def generateRefPropertyTypes(self):
    result = self.fetcher.simpleFetchMethod('ReferencePropertiesV1')
    return refPropertyTypesCompiler.compile(result)

  def generateRefProperties(self):
    result = self.fetcher.simpleFetchMethod('ReferencePropertiesV1')
    return refPropertiesCompiler.compile(result)

  def generateRefLayoutItems(self):
    result = self.fetcher.simpleFetchMethod('ReferenceLayoutItemsV1')
    return refLayoutItemsCompiler.compile(result)

  def generateRefLayoutDetails(self):
    result = self.fetcher.simpleFetchMethod('ReferenceLayoutDetailsV1')
    return refLayoutDetailsCompiler.compile(result)

  def resolve(self, number, dic, dicName):
    if str(number) in dic:
      return dic[str(number)]
    else:
      print('Warning! A ref code was not found in ' + dicName + ': ' + str(number))
      return str(number)

  def resolveRegion(self, number):
    return self.resolve(number, self.regions, 'regions')

  def resolvePropertyType(self, number):
    return self.resolve(number, self.propertyTypes, 'property types')

  def resolveProperty(self, number):
    output = self.resolve(number, self.properties, 'properties')
    # output = output.replace(">=", "min.") # todo: write unit test for this
    return output
  
  def resolvelayoutItem(self, number):
    return self.resolve(number, self.layoutItems, 'layoutItems')

  def resolveLayoutDetail(self, number):
    return self.resolve(number, self.layoutDetails, 'layoutDetails')