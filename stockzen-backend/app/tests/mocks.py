# ==============================================================================
# MOCK DATA
# ==============================================================================
# ------------------------------------------------------------------------------
# User
# ------------------------------------------------------------------------------

user_login = {
    "email": "tester",
    "password": "tester",
}
user_name = {
    "firstName": "tester",
    "lastName": "tester",
}
user_email = "tester"
user_register = {**user_login, **user_name}

# ------------------------------------------------------------------------------
# Portfolio
# ------------------------------------------------------------------------------

portfolio_name = {"portfolioName": "Test Portfolio"}
new_portfolio_name = {"newName": "New Portfolio Name"}


def portfolio_details(id, name="Test Portfolio", order=0):
    portfolio_details = {
        "id": id,
        "portfolioName": name,
        "stockCount": 0,
        "value": 0,
        "change": None,
        "percChange": None,
        "gain": None,
        "percGain": None,
        "order": order,
    }
    return portfolio_details


# ------------------------------------------------------------------------------
# Stock
# ------------------------------------------------------------------------------

non_stock = {"stockPageId": -1}
new_stock_1 = {
    "stockPageId": 1,
    "code": "A",
    "stockName": "Agilent Technologies, Inc.",
}
new_stock_2 = {
    "stockPageId": 20181,
    "code": "TSLA",
    "stockName": "Tesla, Inc.",
}


def stock_details(id, stock, order=0):
    stock_details = {
        "id": id,
        "stockPageId": stock["stockPageId"],
        "code": stock["code"],
        "stockName": stock["stockName"],
        "price": None,
        "change": None,
        "percChange": None,
        "avgPrice": None,
        "unitsHeld": 0,
        "gain": None,
        "percGain": None,
        "value": None,
        "prediction": None,
        "confidence": None,
        "order": order,
    }
    return stock_details


# ------------------------------------------------------------------------------
# Stock Page
# ------------------------------------------------------------------------------
new_stock_page_1 = {
    "id": 1,
    "code": "A",
    "stockName": "Agilent Technologies, Inc.",
    "exchange": "NYQ",
}
uncached_stock_page = {
    **new_stock_page_1,
    "price": None,
    "change": None,
    "percChange": None,
    "prevClose": None,
    "open": None,
    "bid": None,
    "bidSize": None,
    "ask": None,
    "askSize": None,
    "dayHigh": None,
    "dayLow": None,
    "fiftyTwoWeekHigh": None,
    "fiftyTwoWeekLow": None,
    "volume": None,
    "avgVolume": None,
    "marketCap": None,
    "beta": None,
    "longName": None,
    "industry": None,
    "sector": None,
    "website": None,
    "longBusinessSummary": None,
    "prediction": None,
    "confidence": None,
}
