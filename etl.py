from lojaintegrada import Api
from os import environ
from sys import argv, exit
import gspread
import pprint

# Entrypoint
# -------------------------------------------------------------------------------------------------

def main():
  extracted_data = extract()
  transformed_data = transform(extracted_data)

  load(transformed_data)

  print('')
  print('Dados carregados com sucesso!')

# Extract
# -------------------------------------------------------------------------------------------------

def extract():
  print('> Extraindo dados da Loja Integrada...')
  lojaintegrada_orders = get_lojaintegrada_orders()

  return lojaintegrada_orders

def get_lojaintegrada_orders():
  from_date = argv[1]
  order_pages = lojaintegrada_api.get_paid_orders(since_criado=from_date)
  orders = [lojaintegrada_api.get_order(order['numero']) for order_page in order_pages for order in order_page['objects']]

  return orders

# Transform
# -------------------------------------------------------------------------------------------------

def transform(raw_data):
  print('> Transformando dados para o formato desejado...')
  transformed_data = [transform_single_order(order) for order in raw_data]

  return transformed_data

def transform_single_order(order):
  transformed_order = {
    'Numero do pedido': build_order_no(order),
    'Nome do cliente': build_client_name(order),
    'Forma de envio do pedido': build_delivery_method(order),
    'Prazo de postagem': build_deadline(order),
    'Observações do cliente': build_client_comment(order),
    'Produtos': build_products(order),
    'Disponibilidade': build_products_availability(order)
  }

  return transformed_order

def build_order_no(order):
  return order['numero']

def build_client_name(order):
  return order['cliente']['nome']

def build_delivery_method(order):
  primary_method = order['envios'][0]

  return '{} - {}'.format(primary_method['forma_envio']['nome'], primary_method['format_envio']['tipo'])

def build_deadline(order):
  slowest_availability = min([item['disponibilidade'] for item in order['itens']])

  return slowest_availability

def build_client_comment(order):
  return order['cliente_obs']

def build_products(order):
  products = [build_single_product(order_product) for order_product in order['itens']]

  return ',\n'.join(products)

def build_single_product(order_product):
  quantity = int(float(order_product['quantidade']))
  normalized_sku = ' '.join(order_product['sku'].split('-')[1:])
  name = '{} - {}'.format(order_product['nome'], normalized_sku)

  return '{} {}'.format(quantity, name)

def build_products_availability(order):
  products_availability = [build_single_product_availability(order_product) for order_product in order['itens']]

  return ', '.join(products_availability)

def build_single_product_availability(order_product):
  return str(order_product['disponibilidade'])

# Load
# -------------------------------------------------------------------------------------------------

def load(data):
  print('> Carregando dados no Google Sheets...')
  sheet = get_google_sheet()
  previous_data = get_previous_data(sheet)

  filtered_data = filter_new_data(data, previous_data)
  if filtered_data: append_rows(filtered_data, sheet)

def get_google_sheet():
  account = gspread.service_account(filename='google-credential.json')
  sheet = account.open_by_url('https://docs.google.com/spreadsheets/d/1VGcYWX9AugzoLCBVSWxkt3PkMwEiOMlAf_h75SZIcPk/edit#gid=1306728795').sheet1

  return sheet

def get_previous_data(sheet):
  previous_data = sheet.get_all_records()

  return previous_data

def filter_new_data(data, previous_data):
  previous_order_ids = [i['Numero do pedido'] for i in previous_data]
  uniq_data = [line for line in data if line['Numero do pedido'] not in previous_order_ids]

  return uniq_data

def append_rows(data, sheet):
  for row in data:
    append_single_row(row, sheet)

def append_single_row(row, sheet):
  marshaled_row = [
    row['Numero do pedido'],
    row['Nome do cliente'],
    row['Forma de envio do pedido'],
    row['Prazo de postagem'],
    row['Observações do cliente'],
    row['Produtos'],
    row['Disponibilidade'],
   ]

  sheet.append_row(marshaled_row)

# Helpers
# -------------------------------------------------------------------------------------------------

def build_lojaintegrada_api(api_key=environ['LOJA_INTEGRADA_API_KEY'], app_key=environ['LOJA_INTEGRADA_APP_KEY']):
  return Api(api_key, app_key)

lojaintegrada_api = build_lojaintegrada_api()

# Execute
# -------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  main()
