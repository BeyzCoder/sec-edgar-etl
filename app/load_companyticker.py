from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import OperationalError
from datetime import datetime
import time
import json
import os

Base = declarative_base()

DB_CONFIG = [
    os.getenv('DB_USER'),
    os.getenv('DB_PASSWORD'),
    os.getenv('DB_HOST'),
    os.getenv('DB_PORT'),
    os.getenv('DB_NAME'),
]
DB_URL = "postgresql://{}:{}@{}:{}/{}".format(*DB_CONFIG)

class CompanyTicker(Base):
    __tablename__ = "company_tickers"

    id = Column(Integer, primary_key=True)
    sector = Column(String)
    industry = Column(String)
    ticker_symbol = Column(String, unique=True)
    name = Column(String)
    currency = Column(String)

    facts = relationship("CompanyFact", back_populates="company", cascade="all, delete-orphan")


class CompanyFact(Base):
    __tablename__ = "company_facts"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_tickers.id", ondelete="CASCADE"))
    date = Column(Date)
    value = Column(Float)
    statement_type = Column(String)
    key_factor = Column(String)
    form_type = Column(String)

    company = relationship("CompanyTicker", back_populates="facts")


if __name__ == "__main__":
    engine = create_engine(DB_URL)
    for attempt in range(10):
        try:
            with engine.connect() as conn:
                print("Database is ready!")
                break
        except OperationalError:
            print("Database not ready, retrying...")
            time.sleep(5)
    else:
        raise RuntimeError("Database never became available")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)

    with open("edgar_companytickers.json", "r") as f:
        companies = json.load(f)
    
    session = SessionLocal()

    try:
        for ticker_symbol, company_meta in companies.items():
            print(f"Committing: {ticker_symbol}")

            company = CompanyTicker(
                sector=company_meta.get("sector"),
                industry=company_meta.get("industry"),
                ticker_symbol=company_meta.get("ticker"),
                name=company_meta.get("name"),
                currency=company_meta.get("currency"),
            )
            session.add(company)
            session.flush()

            statements = company_meta.get("statements", {})
            for statement_type, key_factors in statements.items():
                for key_factor, values in key_factors.items():
                    for date, value in values.items():
                        fact = CompanyFact(
                            company_id=company.id,
                            date=datetime.strptime(date, "%Y-%m-%d").date(),
                            value=value,
                            statement_type=statement_type.capitalize(),
                            key_factor=key_factor,
                            form_type="Annually"
                        )
                        session.add(fact)

        session.commit()
        print("All tickers data are in the database!")
    
    except Exception as e:
        session.rollback()
        print("ERROR", e)
    
    finally:
        session.close()