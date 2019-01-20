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
    # self.writeDicToFile(self.regions, 'regions')
    # self.writeDicToFile(self.properties, 'properties')
    # self.writeDicToFile(self.layoutItems, 'layoutItems')
    # self.writeDicToFile(self.layoutDetails, 'layoutDetails')
    
  def writeDicToFile(self, dic, name):
    with open('ref_'+name+'.txt', 'w') as file:
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
    return self.resolve(number, self.regions, 'property types')

  def resolveProperty(self, number):
    return self.resolve(number, self.properties, 'properties')
  
  def resolvelayoutItem(self, number):
    return self.resolve(number, self.layoutItems, 'layoutItems')

  def resolveLayoutDetail(self, number):
    return self.resolve(number, self.layoutDetails, 'layoutDetails')