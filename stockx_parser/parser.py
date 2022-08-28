import random
import logging

from stockx_api_client import StockxClient

from stockx_parser import queries

logger = logging.getLogger(__name__)

class StockxParser:

    def __init__(
        self, 
        proxies={}, 
        proxies_list=[{}], 
        gateway=None, 
        rotation_options={'rotation': False, 'random_rotation':False, 'rotation_policy': 'sequential', 'rotation_rand_rate':0.15}
    ):
        
        custom_headers = {
            'accept-language': 'fr-FR',
            'selected-country': 'FR'
        }
        custom_cookies = {
            'language_code': 'fr',
            'stockx_selected_locale': 'fr',
            'stockx_selected_region': 'FR',    
        }
        self._proxies = proxies
        self._proxies_list = proxies_list
        self._proxies_index = 0
        self._rotation = rotation_options.get('rotation')
        self._random_rotation = rotation_options.get('random_rotation')
        self._rotation_rand_rate = rotation_options.get('rotation_rand_rate')
        self._rotation_policy = rotation_options.get('rotation_policy')
        self._client = StockxClient(proxies=proxies, custom_headers=custom_headers, custom_cookies=custom_cookies, gateway=gateway)

    @property
    def next_proxies_index(self):
        if self._rotation_policy == 'random':
            self._proxies_index = random.randint(0, len(self._proxies_list) - 1)
        elif self._rotation_policy == 'sequential':
            self._proxies_index = self._proxies_index + 1 if len(self._proxies_list) - 1 > self._proxies_index else 0
        else:
            self._proxies_index = 0

        return self._proxies_index

    def rotate_proxies(self, proxies=None, proxies_list=None, randomize=False):
        if not self._rotation:
            return
        if randomize:
            if random.random() > self._rotation_rand_rate or not self._random_rotation:
                return
        print('Random' if randomize else '', 'Rotating proxies ...')
        logger.info('Random' if randomize else '', 'Rotating proxies ...')
        new_proxies = proxies
        if proxies_list:
            self._proxies_list = proxies_list

        if proxies:
            self._proxies = proxies 
        else:
            new_proxies = self._proxies_list[self.next_proxies_index]

        print('Setting new proxies: {}'.format(new_proxies))
        logger.info('Setting new proxies: {}'.format(new_proxies))
        self._client.set_proxies(new_proxies)

    def _fetch_products_batch(self, page, limit=17):
        print('Fetching products page {} ...'.format(page))
        logger.info('Fetching products page {} ...'.format(page))
        self.rotate_proxies(randomize=True)
        query = queries.browse_products_query
        query_payload = {
            'operationName': "Browse",
            'query': query,
            'variables': {
                'category': 'sneakers',
                'filters': [
                    {
                        'id': 'browseVerticals',
                        'selectedValues': [
                            'sneakers',
                        ],
                    },
                    {
                        'id': 'currency',
                        'selectedValues': [
                            'EUR',
                        ],
                    },
                ],
                'sort': {
                    'id': 'most-active',
                    'order': 'DESC',
                },
                'page': {
                    'index': page,
                    'limit': limit,
                },
                'currency': 'EUR',
                'country': 'FR',
                'market': 'FR',
            },    
        }

        return self._client.gql.query(query_payload)

    def fetch_products(self, limit=15, multi_threaded=False, start_page=1, stop_page=None):
        products, page = [], start_page
        try:
            res = self._fetch_products_batch(page, limit=limit)
        except Exception as e:
            print('Error {} fetching products page {}'.format(e, page))
            logger.error('Error {} fetching products page {}'.format(e, page))
            return products, page, False
            
        if res.status_code != 200:
            print('Error {} fetching products page {}'.format(res.status_code, page))
            logger.error('Error {} fetching products page {}'.format(res.status_code, page))
            if res.status_code == 403:
                self.rotate_proxies()
            return products, page, res

        edges = res.json()['data']['browse']['results']['edges']
        while len(edges):
            products += edges
            page += 1
            if stop_page is not None and page >= stop_page:
                break
            try:
                res = self._fetch_products_batch(page, limit=limit)
            except Exception as e:
                print('Error {} fetching products page {}'.format(e, page))
                logger.error('Error {} fetching products page {}'.format(e, page))
                return products, page, False
                
            if res.status_code != 200:
                print('Error {} fetching products page {}'.format(res.status_code, page))
                logger.error('Error {} fetching products page {}'.format(res.status_code, page))
                if res.status_code == 403:
                    self.rotate_proxies()                
                return products, page, res
            edges = res.json()['data']['browse']['results']['edges']
        
        return products, page, True

    def fetch_product_price_levels(self, product_url_key, transaction_type, limit=50, page=1, recursive=True):
        self.rotate_proxies(randomize=True)
        custom_headers = {
            "x-user-legacy-price-levels": "legacy"
        }        
        query = queries.get_product_price_levels_query
        query_payload = {
            "operationName": "GetProductPriceLevels",
            "query": query,
            "variables": {
                "country": "FR",
                "currencyCode": "EUR",
                "isVariant": False,
                "limit": limit,
                "page": page,
                "productId": product_url_key,
                "transactionType": transaction_type,
            }            
        }

        res = self._client.gql.query(query_payload, custom_headers=custom_headers)
        if res.status_code != 200:
            print('Error {} fetching product price levels of {}'.format(res.status_code, product_url_key))
            logger.error('Error {} fetching product price levels of {}'.format(res.status_code, product_url_key))
            if res.status_code == 403:
                self.rotate_proxies()
                return self.fetch_product_price_levels(product_url_key, transaction_type, limit=limit, page=page, recursive=recursive)

        return res

    def _fetch_bids_asks_batch(self, page, transaction_type, limit=50, transaction_type_limit=50):
        print('Fetching products bids asks page {} ...'.format(page))
        logger.info('Fetching products bids asks page {} ...'.format(page))
        self.rotate_proxies(randomize=True)
        custom_headers = {
            "x-user-legacy-price-levels": "legacy"
        }        
        query_payload = {
            'operationName': "Browse",
            'query': queries.browse_bids_asks_query,
            'variables': {
                'category': 'sneakers',
                'filters': [
                    {
                        'id': 'browseVerticals',
                        'selectedValues': [
                            'sneakers',
                        ],
                    },
                    {
                        'id': 'currency',
                        'selectedValues': [
                            'EUR',
                        ],
                    },
                ],
                'sort': {
                    'id': 'most-active',
                    'order': 'DESC',
                },
                'page': {
                    'index': page,
                    'limit': limit,
                },
                'currency': 'EUR',
                'country': 'FR',
                'market': 'FR',
                'transactionType': transaction_type,
                'limit': transaction_type_limit
            },    
        }

        return self._client.gql.query(query_payload, custom_headers=custom_headers)

    def fetch_bids_asks(self, transaction_type, limit=50, transaction_type_limit=50, start_page=1, stop_page=None):
        products, page = [], start_page
        if transaction_type not in ['BID', 'ASK']:
            print('Please provide valid transaction type: BID or ASK')
            logger.error('Please provide valid transaction type: BID or ASK')
            return products, page, False
        try:
            res = self._fetch_bids_asks_batch(page, transaction_type, limit=limit, transaction_type_limit=transaction_type_limit)
        except Exception as e:
            print('Error {} fetching products bids asks page {}'.format(e, page))
            logger.error('Error {} fetching products bids asks page {}'.format(e, page))
            return products, page, False

        if res.status_code != 200:            
            print('Error {} fetching products bids asks page {}'.format(res.status_code, page))
            logger.error('Error {} fetching products bids asks page {}'.format(res.status_code, page))
            if res.status_code == 403:
                self.rotate_proxies()
            return products, page, res

        edges = res.json()['data']['browse']['results']['edges']
        while len(edges):
            products += edges
            page += 1
            if stop_page is not None and page >= stop_page:
                break
            try:
                res = self._fetch_bids_asks_batch(page, transaction_type, limit=limit, transaction_type_limit=transaction_type_limit)
            except Exception as e:
                print('Error {} fetching products bids asks page {}'.format(e, page))
                logger.error('Error {} fetching products bids asks page {}'.format(e, page))
                return products, page, False
            if res.status_code != 200:            
                print('Error {} fetching products bids asks page {}'.format(res.status_code, page))
                logger.error('Error {} fetching products bids asks page {}'.format(res.status_code, page))
                if res.status_code == 403:
                    self.rotate_proxies()    
                return products, page, res
            edges = res.json()['data']['browse']['results']['edges']
        
        return products, page, True

    def fetch_product_sales(self, url_key, product_id, limit=50, recursive=True):
        referer = 'https://stockx.com/fr-fr/' + url_key
        product_id = product_id
        params = {
            "limit": str(limit),
            "page": "1",
            "sort": "createdAt",
            "order": "DESC",
            "state": "480",
            "currency": "EUR",
            "country": "FR",
        }
        res = self._client.products.activity(product_id).fetch_list(params=params, custom_headers={'referer': referer})        
        if res.status_code != 200:
            print('Error {} fetching order {}'.format(res.status_code, url_key))
            logger.error('Error {} fetching order {}'.format(res.status_code, url_key))
            if res.status_code == 403:
                self.rotate_proxies()
                return self.fetch_product_sales(url_key, product_id, limit=limit, recursive=recursive)
        return res