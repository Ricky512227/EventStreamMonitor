from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    BigInteger,
    Integer,
    Numeric,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import relationship

BookingBase = declarative_base()


class AeroplaneModel(BookingBase):
    __tablename__ = "aeroplanes"
    ID = Column(
        BigInteger,
        Sequence("aeroplane_id_seq", start=1000),
        primary_key=True
    )
    Model = Column(String(255), nullable=False)
    Manufacturer = Column(String(255), nullable=False)
    YearBuilt = Column(Integer, nullable=False)
    Capacity = Column(Integer, nullable=False)
    FuelCapacity = Column(Numeric(10, 2), nullable=False)
    Status = Column(String(50), nullable=False, default="active")
    UserID = Column(BigInteger, ForeignKey("users.ID"), nullable=True)
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)

    # Indexes
    model_index = Index("idx_model", Model)
    status_index = Index("idx_status", Status)

    def __repr__(self):
        return (
            f"AeroplaneID='{self.ID}', Model='{self.Model}', "
            f"Manufacturer='{self.Manufacturer}', Capacity='{self.Capacity}'"
        )


class FlightModel(BookingBase):
    __tablename__ = "flights"
    ID = Column(
        BigInteger,
        Sequence("flight_id_seq", start=1000),
        primary_key=True
    )
    FlightNumber = Column(String(50), nullable=False, unique=True)
    AeroplaneID = Column(
        BigInteger,
        ForeignKey("aeroplanes.ID"),
        nullable=False
    )
    DepartureAirport = Column(String(100), nullable=False)
    ArrivalAirport = Column(String(100), nullable=False)
    DepartureTime = Column(DateTime, nullable=False)
    ArrivalTime = Column(DateTime, nullable=False)
    AvailableSeats = Column(Integer, nullable=False)
    Price = Column(Numeric(10, 2), nullable=False)
    Status = Column(String(50), nullable=False, default="scheduled")
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)

    # Relationships
    aeroplane = relationship("AeroplaneModel", backref="flights")

    # Indexes
    flight_number_index = Index("idx_flight_number", FlightNumber)
    departure_time_index = Index("idx_departure_time", DepartureTime)
    status_index = Index("idx_flight_status", Status)

    def __repr__(self):
        return (
            f"FlightID='{self.ID}', FlightNumber='{self.FlightNumber}', "
            f"Departure='{self.DepartureAirport}', Arrival='{self.ArrivalAirport}'"
        )


class BookingModel(BookingBase):
    __tablename__ = "bookings"
    ID = Column(
        BigInteger,
        Sequence("booking_id_seq", start=1000),
        primary_key=True
    )
    UserID = Column(BigInteger, nullable=False)  # Reference to user service
    FlightID = Column(
        BigInteger,
        ForeignKey("flights.ID"),
        nullable=False
    )
    NumberOfSeats = Column(Integer, nullable=False)
    TotalPrice = Column(Numeric(10, 2), nullable=False)
    Status = Column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending, confirmed, cancelled
    BookingReference = Column(String(50), nullable=False, unique=True)
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)

    # Relationships
    flight = relationship("FlightModel", backref="bookings")

    # Indexes
    booking_ref_index = Index("idx_booking_reference", BookingReference)
    user_id_index = Index("idx_user_id", UserID)
    status_index = Index("idx_booking_status", Status)
    __table_args__ = (
        UniqueConstraint("BookingReference", name="uq_booking_reference"),
    )

    def __repr__(self):
        return (
            f"BookingID='{self.ID}', BookingReference='{self.BookingReference}', "
            f"UserID='{self.UserID}', Status='{self.Status}'"
        )

