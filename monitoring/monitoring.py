import clickhouse_connect
from datetime import datetime

class Monitoring:
    def __init__(self, host='localhost', port=8123, username='default', password=''):
        self.client = clickhouse_connect.get_client(host=host, port=port, username=username, password=password)

    def create_table(self, table_name, columns):
        columns_with_types = ', '.join([f'{name} {type}' for name, type in columns.items()])
        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types}) ENGINE = MergeTree() ORDER BY tuple()'
        self.client.command(create_table_query)

    def insert_data(self, table_name, data, column_names=None):
        self.client.insert(table_name, data, column_names=column_names)

    def fetch_and_print_table_data(self, table_name):
        result = self.client.query(f'SELECT * FROM {table_name}')
        for row in result.result_rows:
            print(row)

    def format_time_to_datetime(self, timestamp_str):
        return datetime.fromtimestamp(int(timestamp_str) / 1000)


    def insert_orders_history_to_db(self, order_history):
        """
        Добавляет сразу несколько ордеров в кликхаус
        :param order_history: work in bybit only
        """
        data = []
        # print("Check:")
        # print(order_history['result']['list'])
        # Extract relevant data from each order
        for order in order_history['result']['list']:
            data.append((
                order['orderId'],
                order['symbol'],
                float(order['price']),
                float(order['qty']),
                order['side'],
                order['orderType'],
                order['orderStatus'],
                self.format_time_to_datetime(order['createdTime']),
                self.format_time_to_datetime(order['updatedTime'])
            ))

            # Define the column names in the same order as the data
            column_names = ['order_id', 'symbol', 'price', 'qty', 'side', 'order_type', 'order_status', 'created_time',
                            'updated_time']

            # Insert data into the database
            table_name = 'orders'  # Change this to your actual table name
            self.insert_data(table_name, data, column_names)

    def insert_single_order_to_db(self, order):
        """
        Добавляет один ордер в кликхаус
        :param order: data order (dictionary)
        """
        data = [(
            order['orderId'],
            order['symbol'],
            float(order['price']),
            float(order['qty']),
            order['side'],
            order['orderType'],
            order['orderStatus'],
            self.format_time_to_datetime(order['createdTime']),
            self.format_time_to_datetime(order['updatedTime'])
        )]

        column_names = ['order_id', 'symbol', 'price', 'qty', 'side', 'order_type', 'order_status', 'created_time',
                        'updated_time']

        table_name = 'orders'
        self.insert_data(table_name, data, column_names)

