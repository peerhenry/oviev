# Should return a dictionary of number - NL description
def compile(refPropList):
  dic = dict()
  counter = 0
  for typeEntry in refPropList:
    number = typeEntry['TypeNumber']
    dic[str(number)] = extractDutchName(typeEntry)
    counter += 1
  print('compiled '+str(counter)+' property type refs')
  return dic

def extractDutchName(element):
  descriptionArray = element['TypeDescription']
  for langName in descriptionArray:
    if langName['Language'] == 'NL':
      return langName['Description']

# [
# 		{
# 			"TypeNumber": "10",
# 			"TypeDescription": [
# 				{
# 					"Language": "NL",
# 					"Description": "Soort"
# 				},
# 				{
# 					"Language": "FR",
# 					"Description": "Type de bâtiment"
# 				},
# 				{
# 					"Language": "DE",
# 					"Description": "Art"
# 				},
# 				{
# 					"Language": "EN",
# 					"Description": "Type"
# 				},
# 				{
# 					"Language": "IT",
# 					"Description": "Tipo"
# 				},
# 				{
# 					"Language": "ES",
# 					"Description": "Tipo"
# 				},
# 				{
# 					"Language": "PL",
# 					"Description": "Kategoria"
# 				}
# 			],
# 			"Properties": [
# 				{
# 					"Number": "20",
# 					"PropertyDescription": [
# 						{
# 							"Language": "NL",
# 							"Description": "Kasteel"
# 						},
# 						{
# 							"Language": "FR",
# 							"Description": "Château"
# 						},
# 						{
# 							"Language": "DE",
# 							"Description": "Schloss"
# 						},
# 						{
# 							"Language": "EN",
# 							"Description": "Castle"
# 						},
# 						{
# 							"Language": "IT",
# 							"Description": "Castello"
# 						},
# 						{
# 							"Language": "ES",
# 							"Description": "Castillo/Fortaleza"
# 						},
# 						{
# 							"Language": "PL",
# 							"Description": "Zamek"
# 						}
# 					]
# 				},