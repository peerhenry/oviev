def compile(refDetailsList):
  dic = dict()
  counter = 0
  for el in refDetailsList:
    number = el['Number']
    dic[str(number)] = extractDutchName(el)
    counter += 1
  # print('compiled '+str(counter)+' layout detail refs')
  return dic

def extractDutchName(element):
  descriptionArray = element['DetailDescription']
  for langName in descriptionArray:
    if langName['Language'] == 'NL':
      return langName['Description']


# refDetailsList looks like this;

# [
# 		{
# 			"Number": 100,
# 			"DetailDescription": [
# 				{
# 					"Language": "NL",
# 					"Description": "privé"
# 				},
# 				{
# 					"Language": "FR",
# 					"Description": "privé"
# 				},
# 				{
# 					"Language": "DE",
# 					"Description": "alleinige Nutzung"
# 				},
# 				{
# 					"Language": "EN",
# 					"Description": "private"
# 				},
# 				{
# 					"Language": "IT",
# 					"Description": "privato"
# 				},
# 				{
# 					"Language": "ES",
# 					"Description": "privado"
# 				},
# 				{
# 					"Language": "PL",
# 					"Description": "prywatny"
# 				}
# 			]
# 		},