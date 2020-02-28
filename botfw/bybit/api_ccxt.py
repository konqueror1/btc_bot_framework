# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import ArgumentsRequired
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import ExchangeNotAvailable
from ccxt.base.errors import InvalidNonce


class bybit (Exchange):

    def describe(self):
        return self.deep_extend(super(bybit, self).describe(), {
            'id': 'bybit',
            'name': 'Bybit',
            'countries': ['SG'],  # Singapore
            'userAgent': 'sdk_ccxt/bybit_1.0',
            'rateLimit': 100,
            'has': {
                'fetchDepositAddress': False,
                'CORS': False,
                'fetchTickers': True,
                'fetchTicker': True,
                'fetchOHLCV': True,
                'fetchMyTrades': True,
                'fetchTrades': False,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'withdraw': False,
                'fetchDeposits': True,
                'fetchWithdrawals': True,
                'fetchTransactions': False,
            },
            'timeframes': {
                '1m': '1',
                '3m': '3',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '4h': '240',
                '6h': '360',
                '9h': '720',
                '1d': 'D',
                '1M': 'M',
                '1w': 'W',
                '1Y': 'Y',
            },
            'debug': False,  # set True to use testnet
            'urls': {
                'test': {
                    'v2': 'http://api-testnet.bybit.com/v2',
                    'wapi': 'https://api-testnet.bybit.com',
                    'public': 'https://api-testnet.bybit.com/open-api',
                    'private': 'https://api-testnet.bybit.com/open-api',
                },
                'api': {
                    'v2': 'https://api.bybit.com/v2',
                    'wapi': 'https://api.bybit.com',
                    'public': 'https://api.bybit.com/open-api',
                    'private': 'https://api.bybit.com/open-api',
                },
                'logo': 'https://user-images.githubusercontent.com/3198806/66993457-30a52700-f0fe-11e9-810c-a4a51e36fd20.png',
                'www': 'https://www.bybit.com',
                'doc': [
                    'https://github.com/bybit-exchange/bybit-official-api-docs',
                ],
                'fees': 'https://help.bybit.com/hc/en-us/articles/360007291173-Trading-Fee',
            },
            'api': {
                'v2': {
                    'get': [
                        'public/time',
                        'public/symbols',
                        'public/tickers',
                        'public/ticker',
                        'public/kline/list',
                        'public/orderBook/L2',
                        'private/execution/list',
                    ],
                },
                'wapi': {
                    'get': [
                        'position/list',
                    ],
                },
                'private': {
                    'get': [
                        'order/list',
                        'stop-order/list',
                        'wallet/fund/records',
                        'wallet/withdraw/list',
                    ],
                    'post': [
                        'order/create',
                        'order/cancel',
                        'stop-order/create',
                        'stop-order/cancel',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'taker': 0.00075,
                    'maker': -0.00025,
                },
            },
            # exchange-specific options
            'options': {
                'recvWindow': 5 * 1000,  # 5 seconds by default
                'timeDifference': 0,
                'adjustTime': False,  # set True to sync server time before api call
            },
            'exceptions': {
                '-1': ExchangeNotAvailable,
                '20010': InvalidOrder,  # createOrder -> 'invalid qty' or others
                '10002': InvalidNonce,  # 'your time is ahead of server'
                '10003': AuthenticationError,  # api_key invalid,
                '10004': AuthenticationError,  # invalid sign,
                '10005': AuthenticationError,  # permission denied
                '10010': AuthenticationError,  # ip mismatch
            },
        })

    def nonce(self):
        return self.milliseconds() - self.options['timeDifference']

    def load_server_time_difference(self):
        response = self.v2GetPublicTime()
        after = self.milliseconds()
        serverTime = int(response['time_now']) * 1000
        self.options['timeDifference'] = int(after - serverTime)
        return self.options['timeDifference']

    def fetch_markets(self, params={}):
        if self.options['adjustTime']:
            self.load_server_time_difference()
        response = self.v2GetPublicSymbols(params)
        data = self.safe_value(response, 'result', [])
        result = []
        for i in range(0, len(data)):
            market = data[i]
            id = self.safe_string(market, 'name')
            baseId = self.safe_string(market, 'base_currency')
            quoteId = self.safe_string(market, 'quote_currency')
            active = self.safe_value(market, 'active', True)
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'info': market,
            })
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = self.v2GetPublicTickers(self.extend(request, params))
        return self.parse_ticker(response['result'][0])

    def fetch_tickers(self, symbol=None, params={}):
        self.load_markets()
        response = self.v2GetPublicTickers()
        return self.parse_tickers(response['result'])

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        if not('order_id' in list(params.keys())) and (symbol is None):
            raise ArgumentsRequired(self.id + ' fetchMyTrades requires `symbol` or `order_id` param')
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        if since is not None:
            request['startTime'] = self.safe_integer(since / 1000)
        if limit is not None:
            request['limit'] = limit
        response = self.v2GetPrivateExecutionList(self.extend(request, params))
        return self.parse_trades(self.safe_value(response['result'], 'trade_list', []), market, since, limit)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        response = self.v2GetPublicOrderBookL2(self.extend(request, params))
        result = {
            'bids': [],
            'asks': [],
            'timestamp': None,
            'datetime': None,
            'nonce': None,
        }
        data = self.safe_value(response, 'result', [])
        for i in range(0, len(data)):
            order = data[i]
            side = 'asks' if (order['side'] == 'Sell') else 'bids'
            amount = self.safe_float(order, 'size')
            price = self.safe_float(order, 'price')
            if price is not None:
                result[side].append([price, amount])
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        request = {}
        response = self.wapiGetPositionList(self.extend(request, params))
        retData = response['result']
        result = {'info': retData}
        for i in range(0, len(retData)):
            position = retData[i]
            symbol = self.safe_string(position, 'symbol')
            currencyId = self.convert_symbol_to_currency(symbol)
            code = self.safe_currency_code(currencyId)
            account = self.account()
            account['total'] = position['wallet_balance']
            account['used'] = position['position_margin'] + position['occ_closing_fee'] + position['occ_funding_fee'] + position['order_margin']
            result[code] = account
        return self.parse_balance(result)

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'interval': self.timeframes[timeframe],
        }
        if since is None:
            request['from'] = self.seconds() - 86400  # default from 24 hours ago
        else:
            request['from'] = self.truncate(since / 1000, 0)
        if limit is not None:
            request['limit'] = limit  # default == max == 200
        response = self.v2GetPublicKlineList(self.extend(request, params))
        return self.parse_ohlcvs(response['result'], market, timeframe, since, limit)

    def fetch_order(self, id, symbol=None, params={}):
        filter = {
            'order_id': id,
        }
        response = self.fetch_orders(symbol, None, None, self.deep_extend(filter, params))
        numResults = len(response)
        if numResults == 1:
            return response[0]
        raise OrderNotFound(self.id + ': The order ' + id + ' not found.')

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        openStatusesPairs = self.order_statuses('open')
        openStatusKeys = list(openStatusesPairs.keys())
        request = {
            'order_status': ','.join(openStatusKeys),
        }
        if params is not None:
            request = self.deep_extend(params, request)
        return self.fetch_orders(symbol, since, limit, request)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        orders = self.fetch_orders(symbol, since, limit, params)
        return self.filter_by(orders, 'status', 'closed')

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        request = {}
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        request = self.deep_extend(request, params)
        response = self.privateGetOrderList(request)
        return self.parse_orders(self.safe_value(response['result'], 'data', []), market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        request = {
            'symbol': self.market_id(symbol),
            'side': self.capitalize(side),
            'qty': amount,
            'order_type': self.capitalize(type),
        }
        if price is not None:
            request['price'] = price
        response = None
        if ('stop_px' in list(params.keys())) and ('base_price' in list(params.keys())):
            response = self.privatePostStopOrderCreate(self.extend(request, params))
        else:
            response = self.privatePostOrderCreate(self.extend(request, params))
        order = self.parse_order(response['result'])
        id = self.safe_string(order, 'order_id')
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'order_id': id,
        }
        response = None
        if 'stop_px' in params:
            response = self.privatePostStopOrderCancel(self.extend(request, params))
        else:
            response = self.privatePostOrderCancel(self.extend(request, params))
        return self.parse_order(response['result'])

    def fetch_deposits(self, code=None, since=None, limit=None, params={}):
        request = {
            'wallet_fund_type': 'Deposit',
        }
        if params is not None:
            request = self.deep_extend(params, request)
        return self.fetch_fund_records(code, since, limit, request)

    def fetch_withdrawals(self, code=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        currency = None
        if code is not None:
            currency = self.currency(code)
            request['coin'] = currency
        if since is not None:
            request['start_date'] = self.ymd(since)
        if limit is not None:
            request['limit'] = limit
        reqParams = self.extend(request, params)
        response = self.privateGetWalletWithdrawList(reqParams)
        return self.parse_transactions(self.safe_value(response['result'], 'data', []), currency, since, limit)

    def fetch_fund_records(self, code=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        if since is not None:
            request['start_date'] = self.ymd(since)
        if limit is not None:
            request['limit'] = limit
        currency = None
        if code is not None:
            currency = self.currency(code)
            request['coin'] = currency
        reqParams = self.extend(request, params)
        response = self.privateGetWalletFundRecords(reqParams)
        transactions = self.filter_by_array(self.safe_value(response['result'], 'data', []), 'type', ['Withdraw', 'Deposit'], False)
        return self.parse_transactions(transactions, currency, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp(trade, 'exec_time')
        price = self.safe_float(trade, 'exec_price')  # USD
        amount = self.safe_float(trade, 'exec_value')  # BTC/ETH/XRP/EOS
        id = self.safe_string(trade, 'cross_seq')
        order = self.safe_string(trade, 'order_id')
        side = self.safe_string_lower(trade, 'side')
        cost = self.safe_float(trade, 'exec_qty')
        execFee = self.safe_float(trade, 'exec_fee')
        feeRate = self.safe_float(trade, 'fee_rate')
        symbol = None
        marketId = self.safe_string(trade, 'symbol')
        if marketId is not None:
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
                symbol = market['symbol']
            else:
                symbol = marketId
        fee = {
            'cost': execFee,
            'currency': self.convert_symbol_to_currency(symbol),
            'rate': feeRate,
        }
        takerOrMaker = fee['cost'] < 'maker' if 0 else 'taker'
        type = self.safe_string_lower(trade, 'order_type')
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': id,
            'order': order,
            'type': type,
            'takerOrMaker': takerOrMaker,
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'fee': fee,
        }

    def parse_transaction(self, transaction, currency=None):
        id = self.safe_string(transaction, 'id')
        # For deposits, transactTime == timestamp
        # For withdrawals, transactTime is submission, timestamp is processed
        timestamp = self.parse8601(self.safe_string(transaction, 'updated_at'))
        transactTime = self.parse8601(self.safe_string(transaction, 'submited_at'))
        exec_time = self.safe_string(transaction, 'exec_time')  # used for fetchFundRecords
        if exec_time is not None:
            transactTime = self.parse8601(exec_time)
        type = self.safe_string_lower(transaction, 'type')
        if type is None:
            type = 'withdrawal'  # privateGetWithdrawList has no `type`
        type = self.parse_transaction_type(type)
        # Deposits have no from address or to address, withdrawals have both
        address = None
        addressFrom = None
        addressTo = None
        if type == 'withdrawal':
            addressFrom = self.safe_string(transaction, 'address')
            address = addressFrom
        elif type == 'deposit':
            addressTo = self.safe_string(transaction, 'address')
            address = addressTo
        amount = self.safe_float(transaction, 'amount')
        feeCost = self.safe_float(transaction, 'fee')
        currency = self.safe_string(transaction, 'coin')
        fee = {
            'cost': feeCost,
            'currency': currency,
        }
        status = self.safe_string(transaction, 'status')
        if status is not None:
            status = self.parse_transaction_status(status)
        txid = self.safe_string_2(transaction, 'txid', 'tx_id')
        tagTo = self.safe_string(transaction, 'destination_tag')
        return {
            'info': transaction,
            'id': id,
            'txid': txid,
            'timestamp': transactTime,
            'datetime': self.iso8601(transactTime),
            'addressFrom': addressFrom,
            'address': address,
            'addressTo': addressTo,
            'tagFrom': None,
            'tag': tagTo,
            'tagTo': tagTo,
            'type': type,
            'amount': amount,
            'currency': currency,
            'status': status,
            'updated': timestamp,
            'comment': None,
            'fee': fee,
        }

    def convert_symbol_to_currency(self, symbol):
        symbolToCurrency = {
            'BTCUSD': 'BTC',
            'ETHUSD': 'ETH',
            'XRPUSD': 'XRP',
            'EOSUSD': 'EOS',
        }
        return self.safe_string(symbolToCurrency, symbol, symbol)

    def parse_transaction_status(self, status):
        statuses = {
            'Cancelled': 'canceled',
            'Confirmation Email Expired': 'canceled',
            'Transferred successfully': 'ok',
            'Pending Email Confirmation': 'pending',
            'Pending Review': 'pending',
            'Pending Transfer': 'pending',
            'Processing': 'pending',
            'Rejected': 'rejected',
            'Fail': 'failed',
        }
        return self.safe_string(statuses, status, status)

    def parse_transaction_type(self, transType):
        transTypes = {
            'Deposit': 'deposit',
            'Withdraw': 'withdrawal',
            'withdraw': 'withdrawal',
        }
        return self.safe_string(transTypes, transType, transType)

    def parse_order(self, order):
        status = self.parse_order_status(self.safe_string_2(order, 'order_status', 'stop_order_status'))
        symbol = self.find_symbol(self.safe_string(order, 'symbol'))
        timestamp = self.parse8601(self.safe_string(order, 'created_at'))
        lastTradeTimestamp = self.truncate(self.safe_float(order, 'last_exec_time') * 1000, 0)
        qty = self.safe_float(order, 'qty')  # ordered amount in quote currency
        leaveQty = self.safe_float(order, 'leaves_qty')  # leave amount in quote currency
        price = self.safe_float(order, 'price')  # float price in quote currency
        amount = None  # ordered amount of base currency
        filled = self.safe_float(order, 'cum_exec_value')  # filled amount of base currency, not return while place order
        remaining = self.safe_float(order, 'leaves_value')  # leaves_value
        cost = qty - leaveQty  # filled * price
        average = None
        if cost is not None:
            if filled:
                average = cost / filled
        id = self.safe_string_2(order, 'order_id', 'stop_order_id')
        type = self.safe_string_lower(order, 'order_type')
        side = self.safe_string_lower(order, 'side')
        trades = None
        fee = None  # fy_todo {"currency":"xx", "cost":xx, "rate":xx} `cum_exec_fee` not return now
        return {
            'info': order,
            'id': id,
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'lastTradeTimestamp': lastTradeTimestamp,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'cost': cost,
            'average': average,
            'trades': trades,
            'fee': fee,
        }

    def parse_order_status(self, status):
        statuses = self.order_statuses()
        return self.safe_string(statuses, status, status)

    def order_statuses(self, filter=None):
        statuses = {
            'Created': 'created',
            'New': 'open',
            'PartiallyFilled': 'open',
            'Filled': 'closed',
            'Cancelled': 'canceled',
            'Rejected': 'rejected',
            'Untriggered': 'open',
            'Triggered': 'open',
            'Active': 'open',
        }
        if filter is None:
            return statuses
        else:
            ret = {}
            statusKeys = list(statuses.keys())
            for i in range(0, len(statusKeys)):
                if statuses[statusKeys[i]] == filter:
                    ret[statusKeys[i]] = statuses[statusKeys[i]]
            return ret

    def parse_tickers(self, rawTickers, symbols=None):
        tickers = []
        for i in range(0, len(rawTickers)):
            tickers.append(self.parse_ticker(rawTickers[i]))
        return self.filter_by_array(tickers, 'symbol', symbols)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.safe_integer(ticker, 'close_time')
        symbol = self.find_symbol(self.safe_string(ticker, 'symbol'), market)
        last = self.safe_float(ticker, 'last_price')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high_price_24h'),
            'low': self.safe_float(ticker, 'low_price_24h'),
            'bid': self.safe_float(ticker, 'bid_price'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask_price'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': self.safe_float(ticker, 'prev_price_24h'),  # previous day close
            'change': None,
            'percentage': self.safe_float(ticker, 'price_24h_pcnt'),
            'average': None,
            'baseVolume': self.safe_float(ticker, 'turnover_24h'),
            'quoteVolume': self.safe_float(ticker, 'volume_24h'),
            'info': ticker,
        }

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv['open_time'],
            float(ohlcv['open']),
            float(ohlcv['high']),
            float(ohlcv['low']),
            float(ohlcv['close']),
            float(ohlcv['volume']),
        ]

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'ret_code' in response:
            if response['ret_code'] == 0:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = ''
        env = 'api'
        if self.debug:
            env = 'test'
        url = self.urls[env][api] + '/' + path
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        if (api == 'private') or (api == 'wapi') or (path.find('private') >= 0):
            query = self.extend({
                'api_key': self.apiKey,
                'timestamp': self.nonce(),
                'recv_window': self.options['recvWindow'],
            }, params)
            sortedQuery = {}
            queryKeys = list(query.keys())
            queryKeys.sort()
            for i in range(0, len(queryKeys)):
                sortedQuery[queryKeys[i]] = query[queryKeys[i]]
            queryStr = self.rawencode(sortedQuery)
            signature = self.hmac(self.encode(queryStr), self.encode(self.secret))
            queryStr += '&' + 'sign=' + signature
            url += '?' + queryStr
        else:
            if params:
                queryStr = ''
                queryStr += '&' + self.urlencode(params)
                url += '?' + queryStr
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, statusCode, statusText, url, method, responseHeaders, responseBody, response, requestHeaders, requestBody):
        if statusCode >= 500:
            raise ExchangeNotAvailable(self.id + ' ' + statusText)
        ret_code = self.safe_value(response, 'ret_code', -1)
        exceptions = self.exceptions
        if ret_code in exceptions:
            ExceptionClass = exceptions[ret_code]
            raise ExceptionClass(self.id + ' ' + self.json(response))
