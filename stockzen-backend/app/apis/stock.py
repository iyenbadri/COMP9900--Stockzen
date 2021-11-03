import app.utils.crud_utils as util
from app import executor
from app.utils.calc_utils import propagate_portfolio_updates
from app.utils.enums import Status
from flask import request
from flask_login.utils import login_required
from flask_restx import Namespace, Resource, abort, fields, marshal

api = Namespace("stock", description="Stock related operations")

# ==============================================================================
# API Models
# :param attribute is how the db returns a field (so only applies for responses!)
#   used to convert to the the frontend representation, i.e. camelCase
# ==============================================================================

stock_details_response = api.model(
    "Response: Portfolio stock list (/list is in [] form)",
    {
        "id": fields.Integer(required=True, description="stock id"),
        "stockPageId": fields.Integer(
            attribute="stock_page_id", required=True, description="stock page id"
        ),
        "code": fields.String(required=True, description="stock symbol code"),
        "stockName": fields.String(
            attribute="stock_name", required=True, description="stock name"
        ),
        "price": fields.Float(
            required=True,
            description="price from stock_page",
        ),
        "change": fields.Float(required=True, description="daily change from stock_page"),
        "percChange": fields.Float(
            attribute="perc_change",
            required=True,
            description="percentage daily change from stock_page",
        ),
        "avgPrice": fields.Float(
            attribute="avg_price",
            required=True,
            description="average price of bought lots",
        ),
        "gain": fields.Float(required=True, description="capital gain made by stock"),
        "percGain": fields.Float(
            attribute="perc_gain",
            required=True,
            description="percentage capital gain made by stock",
        ),
        "value": fields.Float(required=True, description="stock market value"),
        "prediction": fields.Integer(
            description="ML Classifier prediction on stock price"
        ),
        "confidence": fields.Float(description="Confidence of prediction"),
        "order": fields.Integer(required=True, description="new stock order"),
    },
)

stock_add_request = api.model(
    "Request: Create new stock row within portfolio",
    {
        "stockPageId": fields.Integer(
            required=True, description="stock page id for added stock"
        ),
    },
)

stock_update_request = api.model(
    "Request: Rename stock row",
    {
        "newName": fields.String(required=True, description="new stock name"),
    },
)

stock_reorder_request = api.model(
    "Request: Reorder stocks rows",
    {
        "id": fields.Integer(required=True, description="stock id"),
        "order": fields.Integer(required=True, description="new stock order"),
    },
)


# ==============================================================================
# API Routes/Endpoints
# ==============================================================================


@api.route("/list/<int:portfolioId>")
class StockCRUD(Resource):
    @login_required
    @api.doc(params={"refresh": "refresh data (0 or 1)"})
    @api.marshal_list_with(stock_details_response)
    @api.response(200, "Successfully retrieved list")
    def get(self, portfolioId):
        """List all stocks from a portfolio"""

        stock_list = util.get_stock_list(portfolioId)
        if stock_list == Status.FAIL:
            return abort(500, "Stock list for the portfolio could not be retrieved")

        # We get the query string i.e. ?refresh=<refresh_flag> and convert to bool
        refresh_flag = request.args.get("refresh") == "1"

        propagate_portfolio_updates(
            portfolioId, refresh_data=refresh_flag
        )  # update stock metrics calculations

        return stock_list

    @login_required
    @api.expect([stock_reorder_request])
    @api.response(200, "Successfully updated list order")
    @api.response(409, "Error: Non-unique order numbers")
    def put(self, portfolioId):
        """Update stock list row ordering"""

        reorder_request = marshal(
            request.json, stock_reorder_request
        )  # array of json objects

        # return error if any order is non-unique
        orderList = [json["order"] for json in reorder_request]
        if len(orderList) > len(set(orderList)):
            return abort(409, "Failed because non-unique order numbers were provided")

        if util.reorder_stock_list(portfolioId, reorder_request) == Status.SUCCESS:
            return {"message": "Stock list successfully reordered"}, 200

        return abort(500, "Stock list could not be reordered")


@api.route("/<int:portfolioId>")
class StockCRUD(Resource):
    @login_required
    @api.expect(stock_add_request)
    def post(self, portfolioId):
        """Create a new stock row"""

        json = marshal(request.json, stock_add_request)
        stock_page_id = json["stockPageId"]

        # concurrent request for latest stock data, finishes after response
        executor.submit(util.update_stock_page, stock_page_id)

        if util.add_stock(portfolioId, stock_page_id) == Status.SUCCESS:
            return {"message": "Stock successfully added"}, 200

        return abort(500, "Could not add stock")


@api.route("/<int:stockId>")
class StockCRUD(Resource):
    @login_required
    @api.marshal_with(stock_details_response)
    @api.response(200, "Successfully retrieved stock row data")
    @api.response(404, "Stock not found")
    def get(self, stockId):
        """Fetch data for a stock row within a portfolio"""

        stock_item = util.fetch_stock(stockId)

        if stock_item == Status.FAIL:
            return abort(404, "Stock could not be found")

        return stock_item

    @login_required
    @api.response(200, "Successfully deleted stock")
    def delete(self, stockId):
        """Delete an existing stock row"""

        if util.delete_stock(stockId) == Status.SUCCESS:
            return {"message": "Stock successfully deleted"}, 200

        return abort(500, "Stock could not be deleted")
