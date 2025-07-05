from fastapi import FastAPI, HTTPException, Request, Form, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime, date
import enum
import os

# Database setup
DATABASE_URL = "sqlite:///./booking.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class TicketTypeEnum(enum.Enum):
    VIP = "VIP"
    STANDARD = "Standard"
    ECONOMY = "Economy"

# Database Models
class VenueDB(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    
    # Relationships
    events = relationship("EventDB", back_populates="venue")

class EventDB(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    
    # Relationships
    venue = relationship("VenueDB", back_populates="events")
    bookings = relationship("BookingDB", back_populates="event")

class TicketTypeDB(Base):
    __tablename__ = "ticket_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(TicketTypeEnum), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    
    # Relationships
    bookings = relationship("BookingDB", back_populates="ticket_type")

class BookingDB(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"))
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    booking_date = Column(DateTime, default=datetime.utcnow)
    confirmation_code = Column(String, nullable=False)
    
    # Relationships
    event = relationship("EventDB", back_populates="bookings")
    ticket_type = relationship("TicketTypeDB", back_populates="bookings")

# Pydantic Models
class VenueBase(BaseModel):
    name: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)

class VenueCreate(VenueBase):
    pass

class Venue(VenueBase):
    id: int
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: datetime
    venue_id: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    venue: Optional[Venue] = None
    
    class Config:
        from_attributes = True

class TicketTypeBase(BaseModel):
    name: TicketTypeEnum
    price: float = Field(..., gt=0)
    description: str = Field(..., min_length=1)

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketType(TicketTypeBase):
    id: int
    
    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    event_id: int
    ticket_type_id: int
    customer_name: str = Field(..., min_length=1)
    customer_email: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    quantity: Optional[int] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class Booking(BookingBase):
    id: int
    total_amount: float
    status: BookingStatus
    booking_date: datetime
    confirmation_code: str
    event: Optional[Event] = None
    ticket_type: Optional[TicketType] = None
    
    class Config:
        from_attributes = True

class BookingStats(BaseModel):
    total_bookings: int
    total_events: int
    total_venues: int
    total_revenue: float
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int

class EventRevenue(BaseModel):
    event_id: int
    event_name: str
    total_revenue: float
    total_bookings: int
    confirmed_bookings: int

class VenueOccupancy(BaseModel):
    venue_id: int
    venue_name: str
    capacity: int
    total_bookings: int
    occupancy_rate: float

class AvailableTickets(BaseModel):
    event_id: int
    event_name: str
    venue_capacity: int
    total_booked: int
    available_tickets: int

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Ticket Booking System", description="Manage events, venues, and ticket bookings with relationships")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize sample data
def init_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_venues = db.query(VenueDB).first()
        if existing_venues:
            return
        
        # Add sample venues
        venues = [
            VenueDB(name="Madison Square Garden", location="New York, NY", capacity=20000),
            VenueDB(name="Hollywood Bowl", location="Los Angeles, CA", capacity=17500),
            VenueDB(name="Red Rocks Amphitheatre", location="Morrison, CO", capacity=9525),
        ]
        db.add_all(venues)
        db.commit()
        
        # Add sample ticket types
        ticket_types = [
            TicketTypeDB(name=TicketTypeEnum.VIP, price=199.99, description="VIP experience with premium seating and perks"),
            TicketTypeDB(name=TicketTypeEnum.STANDARD, price=89.99, description="Standard seating with great view"),
            TicketTypeDB(name=TicketTypeEnum.ECONOMY, price=49.99, description="Economy seating, budget-friendly option"),
        ]
        db.add_all(ticket_types)
        db.commit()
        
        # Add sample events
        events = [
            EventDB(name="Rock Concert 2024", description="Amazing rock concert with top bands", 
                   date=datetime(2024, 6, 15, 20, 0), venue_id=1),
            EventDB(name="Classical Music Evening", description="Orchestra performance", 
                   date=datetime(2024, 7, 20, 19, 0), venue_id=2),
            EventDB(name="Jazz Festival", description="Annual jazz festival", 
                   date=datetime(2024, 8, 10, 18, 0), venue_id=3),
        ]
        db.add_all(events)
        db.commit()
        
        # Add sample bookings
        import random
        import string
        
        for i in range(10):
            confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            event_id = random.randint(1, 3)
            ticket_type_id = random.randint(1, 3)
            quantity = random.randint(1, 4)
            
            # Get ticket price
            ticket_type = db.query(TicketTypeDB).filter(TicketTypeDB.id == ticket_type_id).first()
            total_amount = ticket_type.price * quantity
            
            booking = BookingDB(
                event_id=event_id,
                ticket_type_id=ticket_type_id,
                customer_name=f"Customer {i+1}",
                customer_email=f"customer{i+1}@example.com",
                quantity=quantity,
                total_amount=total_amount,
                status=random.choice(list(BookingStatus)),
                confirmation_code=confirmation_code
            )
            db.add(booking)
        
        db.commit()
        print("Sample data initialized!")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize sample data on startup
init_sample_data()

# Helper function to generate confirmation code
def generate_confirmation_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# API Endpoints

# Events
@app.post("/events", response_model=Event, status_code=201)
async def create_event(
    name: str = Form(...),
    description: str = Form(...),
    date: datetime = Form(...),
    venue_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new event"""
    # Check if venue exists
    venue = db.query(VenueDB).filter(VenueDB.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    event_data = EventCreate(name=name, description=description, date=date, venue_id=venue_id)
    db_event = EventDB(**event_data.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events", response_model=List[Event])
async def get_events(db: Session = Depends(get_db)):
    """Get all events"""
    events = db.query(EventDB).all()
    return events

@app.get("/events/{event_id}/bookings", response_model=List[Booking])
async def get_event_bookings(event_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific event"""
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    bookings = db.query(BookingDB).filter(BookingDB.event_id == event_id).all()
    return bookings

@app.get("/events/{event_id}/available-tickets", response_model=AvailableTickets)
async def get_available_tickets(event_id: int, db: Session = Depends(get_db)):
    """Get available tickets for an event"""
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    venue = db.query(VenueDB).filter(VenueDB.id == event.venue_id).first()
    total_booked = db.query(func.sum(BookingDB.quantity)).filter(
        BookingDB.event_id == event_id,
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    available = venue.capacity - total_booked
    
    return AvailableTickets(
        event_id=event_id,
        event_name=event.name,
        venue_capacity=venue.capacity,
        total_booked=total_booked,
        available_tickets=max(0, available)
    )

@app.get("/events/{event_id}/revenue", response_model=EventRevenue)
async def get_event_revenue(event_id: int, db: Session = Depends(get_db)):
    """Calculate total revenue for a specific event"""
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    total_revenue = db.query(func.sum(BookingDB.total_amount)).filter(
        BookingDB.event_id == event_id,
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    total_bookings = db.query(func.count(BookingDB.id)).filter(
        BookingDB.event_id == event_id
    ).scalar() or 0
    
    confirmed_bookings = db.query(func.count(BookingDB.id)).filter(
        BookingDB.event_id == event_id,
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    return EventRevenue(
        event_id=event_id,
        event_name=event.name,
        total_revenue=total_revenue,
        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings
    )

# Venues
@app.post("/venues", response_model=Venue, status_code=201)
async def create_venue(
    name: str = Form(...),
    location: str = Form(...),
    capacity: int = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new venue"""
    venue_data = VenueCreate(name=name, location=location, capacity=capacity)
    db_venue = VenueDB(**venue_data.dict())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

@app.get("/venues", response_model=List[Venue])
async def get_venues(db: Session = Depends(get_db)):
    """Get all venues"""
    venues = db.query(VenueDB).all()
    return venues

@app.get("/venues/{venue_id}/events", response_model=List[Event])
async def get_venue_events(venue_id: int, db: Session = Depends(get_db)):
    """Get all events at a specific venue"""
    venue = db.query(VenueDB).filter(VenueDB.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    events = db.query(EventDB).filter(EventDB.venue_id == venue_id).all()
    return events

@app.get("/venues/{venue_id}/occupancy", response_model=VenueOccupancy)
async def get_venue_occupancy(venue_id: int, db: Session = Depends(get_db)):
    """Get venue occupancy statistics"""
    venue = db.query(VenueDB).filter(VenueDB.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    total_bookings = db.query(func.sum(BookingDB.quantity)).join(EventDB).filter(
        EventDB.venue_id == venue_id,
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    occupancy_rate = (total_bookings / venue.capacity * 100) if venue.capacity > 0 else 0
    
    return VenueOccupancy(
        venue_id=venue_id,
        venue_name=venue.name,
        capacity=venue.capacity,
        total_bookings=total_bookings,
        occupancy_rate=occupancy_rate
    )

# Ticket Types
@app.post("/ticket-types", response_model=TicketType, status_code=201)
async def create_ticket_type(
    name: TicketTypeEnum = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new ticket type"""
    ticket_type_data = TicketTypeCreate(name=name, price=price, description=description)
    db_ticket_type = TicketTypeDB(**ticket_type_data.dict())
    db.add(db_ticket_type)
    db.commit()
    db.refresh(db_ticket_type)
    return db_ticket_type

@app.get("/ticket-types", response_model=List[TicketType])
async def get_ticket_types(db: Session = Depends(get_db)):
    """Get all ticket types"""
    ticket_types = db.query(TicketTypeDB).all()
    return ticket_types

@app.get("/ticket-types/{type_id}/bookings", response_model=List[Booking])
async def get_ticket_type_bookings(type_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific ticket type"""
    ticket_type = db.query(TicketTypeDB).filter(TicketTypeDB.id == type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    
    bookings = db.query(BookingDB).filter(BookingDB.ticket_type_id == type_id).all()
    return bookings

# Bookings
@app.post("/bookings", response_model=Booking, status_code=201)
async def create_booking(
    event_id: int = Form(...),
    ticket_type_id: int = Form(...),
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new booking"""
    # Validate event exists
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Validate ticket type exists
    ticket_type = db.query(TicketTypeDB).filter(TicketTypeDB.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    
    # Check availability
    venue = db.query(VenueDB).filter(VenueDB.id == event.venue_id).first()
    current_bookings = db.query(func.sum(BookingDB.quantity)).filter(
        BookingDB.event_id == event_id,
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    if current_bookings + quantity > venue.capacity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    # Calculate total amount
    total_amount = ticket_type.price * quantity
    
    # Create booking
    booking_data = BookingCreate(
        event_id=event_id,
        ticket_type_id=ticket_type_id,
        customer_name=customer_name,
        customer_email=customer_email,
        quantity=quantity
    )
    
    db_booking = BookingDB(
        **booking_data.dict(),
        total_amount=total_amount,
        confirmation_code=generate_confirmation_code()
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings", response_model=List[Booking])
async def get_bookings(db: Session = Depends(get_db)):
    """Get all bookings with event, venue, and ticket type details"""
    bookings = db.query(BookingDB).all()
    return bookings

@app.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db)
):
    """Update booking details"""
    db_booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    update_data = booking_update.dict(exclude_unset=True)
    
    # If quantity is being updated, recalculate total amount
    if 'quantity' in update_data:
        ticket_type = db.query(TicketTypeDB).filter(TicketTypeDB.id == db_booking.ticket_type_id).first()
        update_data['total_amount'] = ticket_type.price * update_data['quantity']
    
    for field, value in update_data.items():
        setattr(db_booking, field, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancel a booking"""
    db_booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(db_booking)
    db.commit()
    return {"message": "Booking cancelled successfully"}

@app.patch("/bookings/{booking_id}/status", response_model=Booking)
async def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update booking status"""
    db_booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db_booking.status = status_update.status
    db.commit()
    db.refresh(db_booking)
    return db_booking

# Advanced Queries
@app.get("/bookings/search", response_model=List[Booking])
async def search_bookings(
    event: Optional[str] = Query(None, description="Event name to filter by"),
    venue: Optional[str] = Query(None, description="Venue name to filter by"),
    ticket_type: Optional[str] = Query(None, description="Ticket type to filter by"),
    db: Session = Depends(get_db)
):
    """Search bookings by event name, venue, and/or ticket type"""
    query = db.query(BookingDB).join(EventDB).join(VenueDB).join(TicketTypeDB)
    
    if event:
        query = query.filter(EventDB.name.ilike(f"%{event}%"))
    if venue:
        query = query.filter(VenueDB.name.ilike(f"%{venue}%"))
    if ticket_type:
        query = query.filter(TicketTypeDB.name.ilike(f"%{ticket_type}%"))
    
    bookings = query.all()
    return bookings

@app.get("/booking-system/stats", response_model=BookingStats)
async def get_booking_stats(db: Session = Depends(get_db)):
    """Get booking statistics"""
    total_bookings = db.query(func.count(BookingDB.id)).scalar() or 0
    total_events = db.query(func.count(EventDB.id)).scalar() or 0
    total_venues = db.query(func.count(VenueDB.id)).scalar() or 0
    total_revenue = db.query(func.sum(BookingDB.total_amount)).filter(
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    confirmed_bookings = db.query(func.count(BookingDB.id)).filter(
        BookingDB.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    pending_bookings = db.query(func.count(BookingDB.id)).filter(
        BookingDB.status == BookingStatus.PENDING
    ).scalar() or 0
    
    cancelled_bookings = db.query(func.count(BookingDB.id)).filter(
        BookingDB.status == BookingStatus.CANCELLED
    ).scalar() or 0
    
    return BookingStats(
        total_bookings=total_bookings,
        total_events=total_events,
        total_venues=total_venues,
        total_revenue=total_revenue,
        confirmed_bookings=confirmed_bookings,
        pending_bookings=pending_bookings,
        cancelled_bookings=cancelled_bookings
    )

# Web UI route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page"""
    # Get all data for the dashboard
    events = db.query(EventDB).all()
    venues = db.query(VenueDB).all()
    ticket_types = db.query(TicketTypeDB).all()
    bookings = db.query(BookingDB).all()
    
    # Get statistics
    stats = await get_booking_stats(db)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "events": events,
            "venues": venues,
            "ticket_types": ticket_types,
            "bookings": bookings,
            "stats": stats,
            "BookingStatus": BookingStatus,
            "TicketTypeEnum": TicketTypeEnum
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 