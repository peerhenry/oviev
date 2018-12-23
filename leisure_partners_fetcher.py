import requests
import json
import sys
import msvcrt as m
import credentials

class LeisurePartnersFetcher:

  def __init__(self):
    self.loginParams = {
      # 'WebpartnerCode': credentials.WebpartnerCode,
      # 'WebpartnerPassword': credentials.WebpartnerPassword
      'WebpartnerCode': '?',
      'WebpartnerPassword': '?'
    }

  def createRpc(self, method, params):
    output = {
      'jsonrpc': '2.0',
      'method': method,
      'params': params,
      'id': 22298
    }
    return output

  def httpPost(self, url, method, params):
    jsonPayload = self.createRpc(method, params)
    payload = json.dumps(jsonPayload)
    headers = {
      'Content-Type': "application/json",
      'cache-control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return response

  def callLeisurePartners(self, method, params):
    url = 'https://' + method.lower() + '.jsonrpc-partner.net/cgi/lars/jsonrpc-partner/jsonrpc.htm'
    return self.httpPost(url, method, params)

  def handleStatus(self, name, status):
    if status != 200 :
      print('http error during ' + name + ', status: ' + str(status))
      print('Press any key to exit...')
      m.getch()
      sys.exit(0)
  
  def simpleFetchMethod(self, method):
    response = self.callLeisurePartners(method, self.loginParams)
    self.handleStatus(method, response.status_code)
    jsonResult = json.loads(response.text)
    resultList = jsonResult["result"]
    return resultList

  def fetchListOfHouses(self):
    method = 'ListOfHousesV1'
    return self.simpleFetchMethod(method)
  
  def fetchReferenceRegions(self):
    method = 'ReferenceRegionsV1'
    return self.simpleFetchMethod(method)

  def fetchHouseDetails(self, codes, items):
    params = {
      'WebpartnerCode': self.loginParams['WebpartnerCode'],
      'WebpartnerPassword': self.loginParams['WebpartnerPassword'],
      'HouseCodes': codes,
      'Items': items
    }
    response = self.callLeisurePartners('DataOfHousesV1', params)
    status = response.status_code
    if status != 200:
      print('http error during fetchHouseDetails, status: ' + str(status))
      sys.exit(0)
    jsonResult = json.loads(response.text)
    result = jsonResult["result"]
    return result[0]