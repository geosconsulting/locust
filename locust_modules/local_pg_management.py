from sqlalchemy import create_engine, MetaData, Date, Column, Integer, DDL
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import pypostgresql

engine = create_engine('postgresql+psycopg2://postgres@localhost:5432/locust')
conn = engine.connect()
metadata = MetaData()

#Skipping create_engine and metadata
Base = declarative_base()

class MeasureMixin:
    city_id = Column(Integer, not_null=True)
    log_date = Column(Date, not_null=True)
    peaktemp = Column(Integer)
    unitsales = Column(Integer)


class Measure(MeasureMixin, Base):
    __tablename__ = 'measures'
    __table_args__ = {
        postgresql_partition_by: 'RANGE (log_date)'
    }


class Measure2020(MeasureMixin, Base):
    __tablename__ = 'measures2020'

Measure2020.__table__.add_is_dependent_on(Measure.__table__)

event.listen(
    Measure2020.__table__,
    "after_create",
    DDL("""ALTER TABLE measures ATTACH PARTITION measures2020 VALUES FROM ('2020-01-01') TO ('2021-01-01');""")
)