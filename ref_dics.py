import refRegionCompiler
import refPropertiesCompiler
import refLayoutItemsCompiler
import refLayoutDetailsCompiler

class RefDics:
  def __init__(self, fetcher):
    self.fetcher = fetcher
    self.regions = self.generateRefRegions()
    self.properties = self.generateRefProperties()
    self.layoutItems = self.generateRefLayoutItems()
    self.layoutDetails = self.generateRefLayoutDetails()
  
  def generateRefRegions(self):
    result = self.fetcher.simpleFetchMethod('ReferenceRegionsV1')
    return refRegionCompiler.compile(result)
  
  def generateRefProperties(self):
    result = self.fetcher.simpleFetchMethod('ReferencePropertiesV1')
    return refPropertiesCompiler.compile(result)

  def generateRefLayoutItems(self):
    result = self.fetcher.simpleFetchMethod('ReferenceLayoutItemsV1')
    return refLayoutItemsCompiler.compile(result)

  def generateRefLayoutDetails(self):
    result = self.fetcher.simpleFetchMethod('ReferenceLayoutDetailsV1')
    return refLayoutDetailsCompiler.compile(result)

  def resolve(self, number, dic):
    if number in dic:
      return dic[number]
    else:
      print('Warning! A ref code was not found: ' + number)
      return number

  def resolveRegion(self, number):
    return self.resolve(number, self.regions)

  def resolveProperty(self, number):
    return self.resolve(number, self.properties)
  
  def resolvelayoutItem(self, number):
    return self.resolve(number, self.layoutItems)

  def resolveLayoutDetail(self, number):
    return self.resolve(number, self.layoutDetails)