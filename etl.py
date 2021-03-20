from lojaintegrada import Api
from os import environ
from sys import argv

def main():
  lojaintegrada_api = build_lojaintegrada_api()
  lojaintegrada_orders = get_lojaintegrada_orders(lojaintegrada_api)
  print(lojaintegrada_orders)

def build_lojaintegrada_api(apiKey=environ['LOJA_INTEGRADA_API_KEY'], appKey=environ['LOJA_INTEGRADA_APP_KEY']):
  return Api(apiKey, appKey)

def get_lojaintegrada_orders(api):
  from_date = argv[1]
  order_pages = api.get_paid_orders(since_criado=from_date)
  orders = [api.get_order(order['numero']) for order_page in order_pages for order in order_page['objects']]

  return orders

if __name__ == '__main__':
  main()