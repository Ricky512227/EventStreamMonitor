from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, UniqueConstraint, ForeignKey, Index
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import deferred

Base = declarative_base()


# class AerPlaneDBModel(Base):
#     __tablename__ = "AeroPlanes"
#     AeroPlaneID = Column(BigInteger, Sequence('aeroplane_id_seq',start=3000),primary_key=True)
#     AeroPlaneName = Column(String(255), nullable=False)
#     AeroPlaneType = Column(String(255), nullable=False)
#     AeroPlaneMaker = Column(String(255), nullable=False)
#     AeroPlaneModel = Column(String(255), nullable=False)
#     SeatingCapacity = Column(Integer, nullable=False)
#     FuelCapacity = Column(Integer, nullable=False)
#     CreatedAtTime = Column(DateTime, nullable=False)
#     UpdatedAtTime = Column(DateTime, nullable=False)
#
#     def __repr__(self):
#         return f'AeroPlaneID=\'{self.AeroPlaneID}\', AeroPlaneName=\'{self.AeroPlaneName}\',\
#         AeroPlaneType=\'{self.AeroPlaneType}\', AeroPlaneMaker=\'{self.AeroPlaneMaker}\',\
#         AeroPlaneModel=\'{self.AeroPlaneModel}\', SeatingCapacity=\'{self.SeatingCapacity}\',\
#     FuelCapacity =\'{self.FuelCapacity}\', CreatedAtTime=\'{self.CreatedAtTime}\',\
#         CreatedAtTime =\'{self.CreatedAtTime}'
#
#     @classmethod
#     def before_insert(cls, mapper, connection, target):
#         from src import airliner_logger
#         try:
#             airliner_logger.info("Calling before insert ..")
#             airliner_logger.info("Calling [Mapper] before insert :: {0}".format(mapper))
#             airliner_logger.info("Calling [connection] before insert  :: {0}".format(connection))
#             # airliner_logger.info("Inserting [target] record before insert:", target.AeroPlaneID)
#         except Exception as ex:
#             airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
#
#     # @classmethod
#     # def after_insert(cls, mapper, connection, target):
#     #     from src import airliner_logger
#     #     try:
#     #         airliner_logger.info("Calling after insert ..")
#     #         airliner_logger.info("Calling [Mapper] after insert :: {0}".format(mapper))
#     #         airliner_logger.info("Calling [connection] after insert :: {0}".format(connection))
#     #         # airliner_logger.info("Inserting [target] record after insert:", target.AeroPlaneID)
#     #     except Exception as ex:
#     #         airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))


class UsersModel(Base):
    __tablename__ = 'users'
    ID = Column(BigInteger, Sequence('user_id_seq', start=1000), primary_key=True)
    Username = Column(String(255), nullable=False, unique=True)
    FirstName = Column(String(255), nullable=False)
    LastName = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False, unique=True)
    DateOfBirth = Column(String(255), nullable=False)
    Password = deferred(Column(String(255), nullable=False))
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)

    # Setting Index on the 'username' column
    username_index = Index('idx_username', Username)
    # Setting Index on the 'email' column
    email_index = Index('idx_email', Email)
    __table_args__ = (
        UniqueConstraint('Username', 'Email', name='uq_username_email'),
    )


    def __repr__(self):
        return f'UserID=\'{self.ID}\', UserName=\'{self.Username}\', \
        FirstName=\'{self.FirstName}\', LastName=\'{self.LastName}\', \
        Email=\'{self.Email}\', Password=\'{self.Password}\', \
        DateOfBirth=\'{self.DateOfBirth}\', CreatedAt=\'{self.CreatedAt}\', UpdatedAt=\'{self.UpdatedAt}\''

#
# @event.listens_for(AerPlaneDBModel, 'after_insert', propagate=True)
# def after_insert_listener(mapper, connection, target):
#     target.after_insert(mapper, connection, target)
