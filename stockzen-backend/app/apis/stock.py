import app.utils.crud_utils as util
from app.utils import db_utils as db
from app.utils.enums import Status
from flask import request
from flask_login import current_user
from flask_login.utils import login_required
from flask_restx import Namespace, Resource, fields, marshal

api = Namespace("stock", description="Stock related operations")

# ==============================================================================
# API Models
# :param attribute is how the db returns a field (so only applies for responses!)
#   used to convert to the the frontend representation, i.e. camelCase
# ==============================================================================

stock_list_response = api.model(
    "Response: Portfolio stock list",
    {
        "id": fields.Integer(required=True, description="stock id"),
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
        "unitsHeld": fields.Integer(
            attribute="units_held",
            required=True,
            description="number of units currently held",
        ),
        "gain": fields.Float(required=True, description="capital gain made by stock"),
        "percGain": fields.Float(
            attribute="perc_gain",
            required=True,
            description="percentage capital gain made by stock",
        ),
        "value": fields.Float(required=True, description="stock market value"),
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


# ==============================================================================
# API Routes/Endpoints
# ==============================================================================


@api.route("/list/<portfolioId>")
class StockCRUD(Resource):
    @login_required
    @api.marshal_list_with(stock_list_response)
    @api.response(200, "Successfully retrieved list")
    @api.response(404, "User not found")
    def get(self, portfolioId):
        """List all stocks from a portfolio"""

        stock_list = util.get_stock_list(portfolioId)

        return stock_list


@api.route("/<portfolioId>")
class StockCRUD(Resource):
    @login_required
    @api.expect(stock_add_request)
    def post(self, portfolioId):
        """Create a new stock row"""

        json = marshal(request.json, stock_add_request)

        stock_page_id = json["stockPageId"]

        if util.add_stock(portfolioId, stock_page_id) == Status.SUCCESS:
            return {"message": "stock successfully added"}, 200

        return {"message": "Could not add stock"}, 500


# @api.route("/<stockquery>")
# class StockpageCRUD(Resource):
#     @login_required
#     # @api.marshal_list_with(stock_list_response)
#     @api.response(200, "Successfully retrieved list of stocks")
#     @api.response(404, "No results were found")
#     def get(self, stockquery):
#         """List of related stocks Limit(30)"""
#         stock_list = util.search_stock(stockquery)
#         if stock_list == Status.FAIL:
#             return {"message":"Exception occured, check backend logs"},500
#         if stock_list == []:
#             return stock_list,404
#         return stock_list,200


@api.route("/<stockId>")
class StockCRUD(Resource):
    @login_required
    @api.response(200, "Successfully retrieved stock row data")
    @api.response(404, "Stock not found")
    def get(self, stockId):
        """Fetch data for a stock row within a portfolio"""

        stock_item = util.fetch_stock(stockId)

        if stock_item == Status.FAIL:
            return {"message": "stock could not be found"}, 404

        return stock_item

    @login_required
    @api.response(200, "Successfully deleted stock")
    @api.response(404, "Stock not found")
    def delete(self, stockId):
        """Delete an existing stock row"""

        if util.delete_stock(stockId) == Status.SUCCESS:
            return {"message": "stock successfully deleted"}, 200

        return {"message": "stock could not be deleted"}, 500
