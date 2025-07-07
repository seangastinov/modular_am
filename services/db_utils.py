from typing import List
from sqlalchemy import select
from setting.sqlalchemy_config import get_db_session
from setting.model import RegularMarket
import datetime
import logging
from utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def get_regular_market_data_by_security(security_desc: str) -> List[RegularMarket]:
    with get_db_session() as session:
        query = (
            select(RegularMarket)
            .where(RegularMarket.security_desc == security_desc)
            .order_by(RegularMarket.timestamp)
        )
        result = session.execute(query)
        data = result.scalars().all()
        return data

def get_regular_market_all_security_descriptions() -> List[str]:
    with get_db_session() as session:
        query = select(RegularMarket.security_desc).distinct()
        result = session.execute(query)
        return result.scalars().all()
    
def get_regular_market_data_by_date(date: datetime.date) -> List[RegularMarket]:
    with get_db_session() as session:
        query = (
            select(RegularMarket)
            .where(RegularMarket.timestamp >= datetime.datetime.combine(date, datetime.time.min))
            .where(RegularMarket.timestamp < datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time.min))
            .order_by(RegularMarket.timestamp)
        )
        result = session.execute(query)
        data = result.scalars().all()
        return data


def insert_regular_market(data: list[dict]):
    timestamp = datetime.datetime.now()
    
    with get_db_session() as session:
        records_to_insert = []
        updated_count = 0
        for item in data:
            try:
                security_desc = item.get("Security Description")
                trades = int(item.get("Trades"))
                tta = float(item.get("TTA"))
                open_price = float(item.get("Open"))
                high = float(item.get("High"))
                low = float(item.get("Low"))
                ltp = float(item.get("LTP"))
                lty = float(item.get("LTY"))
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing data for security '{security_desc}': {e}")
                continue
            if (
                security_desc is None or 
                trades is None or  
                tta is None or  
                open_price is None or  
                high is None or  
                low is None or  
                ltp is None or 
                lty
            ):
                logger.warning(f"Missing data for security '{security_desc}'. Skipping record.")
                continue

            # Get the latest record for this security
            latest = (
                session.query(RegularMarket)
                .filter_by(security_desc=security_desc)
                .order_by(RegularMarket.timestamp.desc())
                .first()
            )

            if latest and latest.timestamp.date() == timestamp.date():
                if (
                    latest.trades != trades or
                    latest.tta != tta or
                    latest.open != open_price or
                    latest.high != high or
                    latest.low != low or
                    latest.ltp != ltp or
                    latest.lty != lty
                ):
                # If a record from the same day exist and data is different, update the existing record
                    latest.trades = trades
                    latest.tta = tta
                    latest.open = open_price
                    latest.high = high
                    latest.low = low
                    latest.ltp = ltp
                    latest.lty = lty
                    latest.timestamp = timestamp
                    updated_count += 1
            else:
                # Otherwise, create a new record to be inserted
                record = RegularMarket(
                    security_desc=security_desc,
                    trades=trades,
                    tta=tta,
                    open=open_price,
                    high=high,
                    low=low,
                    ltp=ltp,
                    lty=lty,
                    timestamp=timestamp
                )
                records_to_insert.append(record)
        
        if records_to_insert:
            session.add_all(records_to_insert)
        
        try:
            if records_to_insert or updated_count > 0:
                session.commit()
                logger.info(f"Committed {len(records_to_insert)} new and {updated_count} updated records.")
            else:
                logger.info("No new or updated records to commit.")
        except Exception as e:
            logger.error(f"Error committing records: {e}")
            raise