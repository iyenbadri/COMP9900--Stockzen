import inspect
import os
from datetime import datetime
from itertools import repeat
from typing import Sequence

from app import executor
from app.config import TOP_STOCKS_INTERVAL
from app.models.schema import Challenge, ChallengeEntry, StockPage
from app.utils import api_utils
from sqlalchemy.orm import load_only

from .enums import Status

# ==============================================================================
# For generic or shared helper functions
# ==============================================================================

# Nice error debug message printing
def debug_exception(error, suppress=False):
    if os.environ.get("FLASK_ENV") == "development":
        print(
            f"{type(error).__name__} at line {error.__traceback__.tb_lineno} of {inspect.stack()[1].filename }: {error}"
        )
    if not suppress:
        raise error


# Convert stock_page_id to code/symbol
def id_to_code(stock_page_id: int):
    """Converts a stock page id to stock code using the StockPage table
    Fails if not exactly one stock is found"""
    try:
        return (
            StockPage.query.options(load_only(StockPage.code))
            .filter_by(id=stock_page_id)
            .one()
            .code
        )
    except Exception as e:
        debug_exception(e)


# ------------------------------------------------------------------------------
# Bulk Fetch Utils
# ------------------------------------------------------------------------------


def bulk_stock_fetch(sym_list: Sequence[str], await_all: bool = False):
    """Update all stocks from a list of symbols"""
    # convert symbol list to stock_page_id list
    tuple_list = (
        StockPage.query.options(load_only(StockPage.id, StockPage.code))
        .filter(StockPage.code.in_(sym_list))
        .with_entities(StockPage.id)
        .all()
    )
    id_list = [tuple[0] for tuple in tuple_list]  # where tuple[0] -> stock_page_id

    # concurrently fetch api data to update each stock page
    # pass longer update interval so app does not request bulk from yfinance too often
    results = executor.map(
        api_utils.api_stock_request, id_list, repeat(TOP_STOCKS_INTERVAL)
    )
    if await_all:
        list(results)  # use the result to force program to wait before continuing
        print("All concurrent results returned, continuing...")


def get_open_challenge():
    """Return id and start date of active challenge, or None if not exist"""
    challenge = (
        Challenge.query.filter_by(is_open=True).order_by(Challenge.id.desc()).first()
    )
    if not challenge:
        return None, None
    return challenge.id, challenge.start_date


def get_prev_challenge():
    """Return id and start date of previous challenge, or None if not exist"""
    challenge = (
        Challenge.query.filter_by(is_active=False).order_by(Challenge.id.desc()).first()
    )
    if not challenge:
        return None, None
    return challenge.id, challenge.start_date


def get_closing_challenge():
    """Return id and start date of challenge that is_active but not is_open, or None if not exist"""
    challenge = (
        Challenge.query.filter_by(is_active=True, is_open=False)
        .order_by(Challenge.id.desc())
        .first()
    )
    if not challenge:
        return None, None
    return challenge.id, challenge.start_date


def bulk_challenge_fetch(await_all: bool = False):
    """Function for challenge script to call that caches perc_change for all challenge stocks"""

    prev_challenge_id, prev_start_date = get_closing_challenge()

    unique_stock_ids = (
        ChallengeEntry.query.filter(ChallengeEntry.challenge_id == prev_challenge_id)
        .with_entities(ChallengeEntry.stock_page_id)
        .distinct(ChallengeEntry.stock_page_id)
        .all()
    )
    unique_stock_ids = [tuple[0] for tuple in unique_stock_ids]
    print(f"Fetching challenge data for stockPageIds: {unique_stock_ids}")

    # concurrently fetch api data to update stock page over the Challenge period
    from stockzen import app

    with app.test_request_context():  # workaround to allow for requests outside the app context
        results = executor.map(
            api_utils.api_history_request, unique_stock_ids, repeat(prev_start_date)
        )

    if await_all:
        list(results)  # use the result to force program to wait before continuing
        print("All concurrent Challenge results returned, continuing...")


def is_valid_challenge(challenge_id) -> Status:
    try:
        challenge = Challenge.query.filter_by(id=challenge_id).one()
        if datetime.now() < challenge.start_date and challenge.is_open == True:
            return Status.VALID
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL
