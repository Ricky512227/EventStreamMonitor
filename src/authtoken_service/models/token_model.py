from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, BigInteger, Index
from sqlalchemy.schema import Sequence, UniqueConstraint

Base = declarative_base()
class TokensModel(Base):
    __tablename__ = 'tokens'
    ID = Column(BigInteger, Sequence('token_id_seq',start=2000), primary_key=True)
    UserID = Column(BigInteger, unique=True, nullable=False)
    Token = Column(String(512), unique=True, nullable=False)
    Expiry = Column(String(255), nullable=False)
    CreatedAt = Column(String(255), nullable=False)
    UpdatedAt = Column(String(255), nullable=False)

    # Setting Index on the 'username' column
    userid_index = Index('idx_userid', UserID)
    # Setting Index on the 'email' column
    token_index = Index('idx_token', Token)
    __table_args__ = (
        UniqueConstraint('UserID', 'Token', name='uq_userid_token'),
    )


    def __repr__(self):
        return f'TokenID=\'{self.ID}\', UserID=\'{self.UserID}\', \
        Token=\'{self.Token}\', Expiry=\'{self.Expiry}\', \
        CreatedAt=\'{self.CreatedAt}\', UpdatedAt=\'{self.UpdatedAt}\''


# @event.listens_for(AerPlaneDBModel, 'before_insert', propagate=True)
# def before_insert_listener(mapper, connection, target):
#     target.before_insert(mapper, connection, target)
#
#
# @event.listens_for(AerPlaneDBModel, 'after_insert', propagate=True)
# def after_insert_listener(mapper, connection, target):
#     target.after_insert(mapper, connection, target)












