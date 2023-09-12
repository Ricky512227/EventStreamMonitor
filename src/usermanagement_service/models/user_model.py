from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, UniqueConstraint, ForeignKey, Index
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import deferred

Base = declarative_base()



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

