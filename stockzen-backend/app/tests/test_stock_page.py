import app.tests.mocks as mock
import app.tests.utils as utils


def test_stock_page_endpoints(auth_client):
    client = auth_client

    # --------------------------------------------------------------------------
    # Stock Page details
    # --------------------------------------------------------------------------
    utils.net_blocker(block=True)
    response = client.get("/stock-page/1")
    # Uncached stock page at the start
    assert response.status_code == 200
    assert response.json == mock.uncached_stock_page
    utils.net_blocker(block=False)

    response = client.get("/stock-page/-1")
    # Non-existent stock page
    assert response.status_code == 404

    response = client.get("/stock-page/1")
    # Test successful fetch of uncached stock page
    assert response.status_code == 200
    assert response.json != mock.uncached_stock_page
    # sample test that returned data is not empty
    assert response.json["price"] != None
    assert response.json["prevClose"] != None
    assert response.json["longName"] != None

    cached_response = response.json

    # Test whether cached response is returned
    utils.net_blocker(block=True)
    response = client.get("/stock-page/1")
    # Cached stock page returned
    assert response.status_code == 200
    assert response.json == cached_response
    utils.net_blocker(block=False)


def test_stock_history_endpoints(auth_client):
    client = auth_client
    # --------------------------------------------------------------------------
    # Stock History endpoint
    # --------------------------------------------------------------------------
    utils.net_blocker(block=True)
    response = client.get("/stock-page/14/history")
    # Fail to retrieve if no network and no cached data
    assert response.status_code == 500
    utils.net_blocker(block=False)

    response = client.get("/stock-page/14/history")
    # should retrieve from yfinance (and then cache the data)
    assert response.status_code == 200
    history = response.json
    assert len(history) > 250  # should have > 250 && < 260 trade days
    assert len(history) < 260
    assert history[0]["date"] != None  # date is provided

    utils.net_blocker(block=True)
    response = client.get("/stock-page/14/history")
    # no network, should retrieve from cache
    assert response.status_code == 200
    assert response.json == history  # cached data should be the same
    utils.net_blocker(block=False)


def test_top_performer_endpoint(auth_client):
    client = auth_client
    # --------------------------------------------------------------------------
    # Top Performers endpoint
    # --------------------------------------------------------------------------
    response = client.get("/stock-page/top")
    # None to start with
    assert response.status_code == 200
    assert response.json == []

    # Add predetermined stock_page data
    expected = utils.populate_top_stocks()

    response = client.get("/stock-page/top")
    # Successfully return top stocks in the correct order
    assert response.status_code == 200
    assert response.json == expected
