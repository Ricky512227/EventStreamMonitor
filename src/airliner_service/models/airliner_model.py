import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, ForeignKeyConstraint, ForeignKey
from sqlalchemy.schema import Sequence
from sqlalchemy import event
from sqlalchemy.orm import relationship, deferred

Base = declarative_base()
class AerPlaneDBModel(Base):
    __tablename__ = "AeroPlanes"
    AeroPlaneID = Column(BigInteger, Sequence('aeroplane_id_seq',start=3000),primary_key=True)
    AeroPlaneName = Column(String(255), nullable=False)
    AeroPlaneType = Column(String(255), nullable=False)
    AeroPlaneMaker = Column(String(255), nullable=False)
    AeroPlaneModel = Column(String(255), nullable=False)
    SeatingCapacity = Column(Integer, nullable=False)
    FuelCapacity = Column(Integer, nullable=False)
    CreatedAtTime = Column(DateTime, nullable=False)
    UpdatedAtTime = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'AeroPlaneID=\'{self.AeroPlaneID}\', AeroPlaneName=\'{self.AeroPlaneName}\',\
        AeroPlaneType=\'{self.AeroPlaneType}\', AeroPlaneMaker=\'{self.AeroPlaneMaker}\',\
        AeroPlaneModel=\'{self.AeroPlaneModel}\', SeatingCapacity=\'{self.SeatingCapacity}\',\
    FuelCapacity =\'{self.FuelCapacity}\', CreatedAtTime=\'{self.CreatedAtTime}\',\
        CreatedAtTime =\'{self.CreatedAtTime}'

    @classmethod
    def before_insert(cls, mapper, connection, target):
        from src import airliner_logger
        try:
            airliner_logger.info("Calling before insert ..")
            airliner_logger.info("Calling [Mapper] before insert :: {0}".format(mapper))
            airliner_logger.info("Calling [connection] before insert  :: {0}".format(connection))
            # airliner_logger.info("Inserting [target] record before insert:", target.AeroPlaneID)
        except Exception as ex:
            airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    @classmethod
    def after_insert(cls, mapper, connection, target):
        from src import airliner_logger
        try:
            airliner_logger.info("Calling after insert ..")
            airliner_logger.info("Calling [Mapper] after insert :: {0}".format(mapper))
            airliner_logger.info("Calling [connection] after insert :: {0}".format(connection))
            # airliner_logger.info("Inserting [target] record after insert:", target.AeroPlaneID)
        except Exception as ex:
            airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

@event.listens_for(AerPlaneDBModel, 'before_insert', propagate=True)
def before_insert_listener(mapper, connection, target):
    target.before_insert(mapper, connection, target)


@event.listens_for(AerPlaneDBModel, 'after_insert', propagate=True)
def after_insert_listener(mapper, connection, target):
    target.after_insert(mapper, connection, target)












