from datetime import datetime

from app import db
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
from werkzeug.security import check_password_hash, generate_password_hash

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

# SQL uses implicit auto-increment, no need to specify for non-composite PK


class User(UserMixin, db.Model):
    """SQLAlchemy ORM class for user object ̦

    Inherits from UserMixin for default Flask-Login user states.
        Note:   Default ID for login management is User ID (PK),
                override get_id() to use an alternative ID
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(40), unique=True)
    first_name = Column(String(40))
    last_name = Column(String(40))
    password_hash = Column(String(110))
    validated = Column(Boolean, default=True)

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    # Relationships
    # one-to-many user:portfolios
    portfolios = relationship(
        "Portfolio",
        backref=backref("user", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",  # want children/disassociated children to be removed on delete as well
    )
    stocks = relationship(
        "Stock",
        backref=backref("user", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )
    lots_bought = relationship(
        "LotBought",
        backref=backref("user", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )
    lots_sold = relationship(
        "LotSold",
        backref=backref("user", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, first_name={self.first_name}, last_name{self.last_name}, email={self.email})>"


class Portfolio(db.Model):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_name = Column(String(50), nullable=False)
    stock_count = Column(Integer, default=0)  # count(stocks)
    value = Column(Float)  # sum(stocks.value)
    change = Column(Float)  # sum(stocks.change)
    perc_change = Column(Float)  # portfolios.change / portfolios.value
    gain = Column(Float)  # sum(stocks.gain)
    perc_gain = Column(Float)  # portfolios.gain / portfolios.value
    order = Column(Integer, nullable=False, default=0)  # track row order, default to top
    last_updated = Column(DateTime, default=datetime.now())

    # Relationships
    # one-to-many portfolio:stocks
    stocks = relationship(
        "Stock",
        backref=backref("portfolio", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, portfolio_name={self.portfolio_name}, stock_count={self.stock_count})>"


class Stock(db.Model):
    # Columns to be returned from a JOIN:
    # --------------------------------------------------------------------------
    # code = Column(String(6))
    # stock_name = Column(String(40))
    # price = Column(Float)  # = stock_pages.price
    # change = Column(Float)  # = stock_pages.change
    # perc_change = Column(Float)  # = stock_pages.perc_change

    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    stock_page_id = Column(
        Integer, ForeignKey("stock_pages.id"), nullable=False
    )  # to get current price, change, percent_change, prediction, confidence
    avg_price = Column(Float)  # = bought.avg_price
    gain = Column(Float)  # (stocks.price - bought.avg_price) * stocks.units_held
    perc_gain = Column(Float)  # stocks.gain / (stocks.units_held * bought.avg_price)
    value = Column(Float)  # stocks.units_held * stocks.current_price
    order = Column(Integer, nullable=False, default=0)  # track row order, default to top
    last_updated = Column(DateTime, default=datetime.now())

    # Relationships
    # one-to-many stock:lots
    lots_bought = relationship(
        "LotBought",
        backref=backref("stock", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )
    lots_sold = relationship(
        "LotSold",
        backref=backref("stock", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )
    price_alert = relationship(
        "PriceAlert",
        backref=backref("stock", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )

    # Unique Constraints (multiple column)
    UniqueConstraint(user_id, portfolio_id, stock_page_id)


class LotBought(db.Model):
    __tablename__ = "lots_bought"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    trade_date = Column(DateTime, nullable=False)  # <user>
    units = Column(Integer, nullable=False, default=0)  # <user>
    unit_price = Column(Float, nullable=False)  # <user>
    value = Column(Float)  # stocks.price * bought.unit_price
    change = Column(Float)  # bought.units * stock.change
    last_updated = Column(DateTime, default=datetime.now())


class LotSold(db.Model):
    __tablename__ = "lots_sold"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    trade_date = Column(DateTime, nullable=False)  # <user>
    units = Column(Integer, nullable=False, default=0)  # <user>
    unit_price = Column(Float, nullable=False)  # <user>
    amount = Column(Float)  # sold.units * sold.unit_price
    realised = Column(Float)  # sold.units * (sold.unit_price - stock.avg_price)
    last_updated = Column(DateTime, default=datetime.now())


class StockPage(db.Model):
    __tablename__ = "stock_pages"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code = Column(String(6), unique=True)
    stock_name = Column(String(40))
    exchange = Column(String(20))
    price = Column(Float)
    change = Column(Float)
    perc_change = Column(Float)
    prev_close = Column(Float)
    prediction = Column(Integer)  # -1 for down, 0 no change, 1 for up
    confidence = Column(Float)
    last_updated = Column(DateTime)  # let this be NULL and add timestamp after update
    info = Column(String, default="{}")  # JSON-string of all company info

    # Relationships
    # one-to-many stock_pages:stocks
    stocks = relationship(
        "Stock",
        backref=backref("stock_pages", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )
    # one-to-many stock_pages:history
    history = relationship(
        "History",
        backref=backref("stock_pages", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )


class History(db.Model):
    # 1-yr historical data for each stock
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    stock_page_id = Column(Integer, ForeignKey("stock_pages.id"), nullable=False)
    history = Column(String, nullable=False)


# ------------------------------------------------------------------------------
# Price Alert tables
# ------------------------------------------------------------------------------


class PriceAlert(db.Model):
    __tablename__ = "price_alerts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, unique=True)
    high_threshold = Column(Float)
    low_threshold = Column(Float)
    user_save_time = Column(DateTime)
    is_high_threshold_alerted = Column(Boolean)
    is_low_threshold_alerted = Column(Boolean)
    last_check_time = Column(DateTime)


# ------------------------------------------------------------------------------
# Portfolio Challenge tables
# ------------------------------------------------------------------------------

# Holds Portfolio Challenge round info
class Challenge(db.Model):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(
        Boolean, default=False
    )  # whether challenge is active (end_date not reached yet)
    is_open = Column(
        Boolean, default=False
    )  # whether submissions are open (is_active == True and start_date not reached yet)

    # Relationships
    # one-to-many challenges:entries
    entries = relationship(
        "ChallengeEntry",
        backref=backref("challenges", lazy="select"),
        lazy="select",
        cascade="all, delete, delete-orphan",
    )


# Holds Portfolio Challenge entries
class ChallengeEntry(db.Model):
    __tablename__ = "challenge_entries"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_page_id = Column(Integer, ForeignKey("stock_pages.id"), nullable=False)
    code = Column(String)  # stock symbol
    start_price = Column(Float)
    end_price = Column(Float)
    perc_change = Column(Float)

    # Unique Constraints (multiple column)
    UniqueConstraint(challenge_id, user_id, stock_page_id)
    # NOTE: challenge_id and user_id unique constraint is enforced in the CRUD function
    # to allow for a more informative error message to the frontend
