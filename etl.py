from lojaintegrada import Api
from os import environ
from sys import argv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pprint

def build_lojaintegrada_api(api_key=environ['LOJA_INTEGRADA_API_KEY'], app_key=environ['LOJA_INTEGRADA_APP_KEY']):
  return Api(api_key, app_key)

lojaintegrada_api = build_lojaintegrada_api()

def main():
  extracted_data = extract_data()
  transformed_data = transform_data(extracted_data)
  google_credentials = build_google_credentials()
  google_sheet = build_google_client(google_credentials)

  load_data(transformed_data, google_sheet)

def extract_data():
  lojaintegrada_orders = get_lojaintegrada_orders()

  return lojaintegrada_orders

def get_lojaintegrada_orders():
  from_date = argv[1]
  order_pages = lojaintegrada_api.get_paid_orders(since_criado=from_date)
  orders = [lojaintegrada_api.get_order(order['numero']) for order_page in order_pages for order in order_page['objects']]

  return orders

def transform_data(raw_data):
  transformed_data = [transform_single_order(order) for order in raw_data]

  return transformed_data

def transform_single_order(order):
  transformed_order = {
    'order_no': build_order_no(order),
    'client_name': build_client_name(order),
    'delivery_method': build_delivery_method(order),
    'deadline': build_deadline(order),
    'client_comment': build_client_comment(order),
    'products': build_products(order),
    'products_availability': build_products_availability(order)
  }

  return transformed_order

def build_order_no(order):
  return order['numero']

def build_client_name(order):
  return order['cliente']['nome']

def build_delivery_method(order):
  primary_method = order['envios'][0]
  
  return primary_method['forma_envio']['tipo']

def build_deadline(order):
  slowest_availability = min([item['disponibilidade'] for item in order['itens']])

  return slowest_availability

def build_client_comment(order):
  return order['cliente_obs']

def build_products(order):
  products = [build_single_product(order_product) for order_product in order['itens']]

  return ',\n'.join(products)

def build_single_product(order_product):
  id = order_product['produto'].split('/')[-1]
  product = lojaintegrada_api.get_product(id)
  quantity = int(float(order_product['quantidade']))

  return '{} {}'.format(quantity, product['nome'])

def build_products_availability(order):
  products_availability = [build_single_product_availability(order_product) for order_product in order['itens']]

  return ', '.join(products_availability)

def build_single_product_availability(order_product):
  return str(order_product['disponibilidade'])

def build_google_credentials():
  print('ok')

def build_google_client(credentials):
  print(credentials)

def load_data(data, sheet):
  # https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
  print(data)
  print(sheet)

if __name__ == '__main__':
  main()