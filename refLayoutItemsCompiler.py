# Should return a dictionary of number - NL description
# for example: 208 - Tussenetage
def compile(refItemsList):
  dic = dict()
  counter = 0
  for typeEntry in refItemsList:
    itemsList = typeEntry['Items']
    for item in itemsList:
      number = item['Number']
      dic[str(number)] = extractDutchName(item)
      counter += 1
  # print('compiled '+str(counter)+' layout item refs')
  return dic

def extractDutchName(element):
  descriptionArray = element['Description']
  for langName in descriptionArray:
    if langName['Language'] == 'NL':
      return langName['Description']

# refItemsList looks like this;

# [
# 		{
# 			"Type": 50,
# 			"Description": [
# 				{
# 					"Language": "NL",
# 					"Description": "Verdiepingen"
# 				},
# 				{
# 					"Language": "FR",
# 					"Description": "Planchers"
# 				},
# 				{
# 					"Language": "DE",
# 					"Description": "Stockwerke"
# 				},
# 				{
# 					"Language": "EN",
# 					"Description": "Floors"
# 				},
# 				{
# 					"Language": "IT",
# 					"Description": "Piani"
# 				},
# 				{
# 					"Language": "ES",
# 					"Description": "Pisos"
# 				},
# 				{
# 					"Language": "PL",
# 					"Description": "Podłogi"
# 				}
# 			],
# 			"Items": [
# 				{
# 					"Number": 200,
# 					"Description": [
# 						{
# 							"Language": "NL",
# 							"Description": "Parterre"
# 						},
# 						{
# 							"Language": "FR",
# 							"Description": "Rez-de-chaussée"
# 						},
# 						{
# 							"Language": "DE",
# 							"Description": "Parterre"
# 						},
# 						{
# 							"Language": "EN",
# 							"Description": "Ground floor"
# 						},
# 						{
# 							"Language": "IT",
# 							"Description": "Pianterreno"
# 						},
# 						{
# 							"Language": "ES",
# 							"Description": "Planta baja"
# 						},
# 						{
# 							"Language": "PL",
# 							"Description": "Parter"
# 						}
# 					]
# 				},