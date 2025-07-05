# Ticket Booking System (Q3)

A comprehensive FastAPI application for managing ticket bookings with database relationships between Events, Venues, Ticket Types, and Bookings.

## Features

### Core Functionality
- **Event Management**: Create and manage events with venue associations
- **Venue Management**: Add venues with capacity tracking
- **Ticket Type Management**: Configure different ticket types (VIP, Standard, Economy) with pricing
- **Booking System**: Handle ticket bookings with capacity validation and pricing calculations

### Database Relationships
- **One-to-Many**: Event → Bookings, Venue → Events, Ticket Type → Bookings
- **Many-to-One**: Bookings → Event, Events → Venue, Bookings → Ticket Type
- **Foreign Key Constraints**: Prevents invalid bookings with non-existent references
- **Cascade Operations**: Proper handling of related data deletions

### Advanced Features
- **Capacity Management**: Real-time venue capacity tracking and enforcement
- **Revenue Tracking**: Calculate revenue by event and overall system
- **Booking Status Management**: Track booking states (pending, confirmed, cancelled)
- **Search Functionality**: Find bookings by event, venue, or ticket type
- **Statistics Dashboard**: Comprehensive analytics and reporting
- **Occupancy Tracking**: Monitor venue utilization rates

## API Endpoints

### Events
- `POST /events` - Create new event
- `GET /events` - Get all events
- `GET /events/{event_id}/bookings` - Get bookings for specific event
- `GET /events/{event_id}/available-tickets` - Get available tickets for event
- `GET /events/{event_id}/revenue` - Calculate event revenue

### Venues
- `POST /venues` - Create new venue
- `GET /venues` - Get all venues
- `GET /venues/{venue_id}/events` - Get events at specific venue
- `GET /venues/{venue_id}/occupancy` - Get venue occupancy statistics

### Ticket Types
- `POST /ticket-types` - Create new ticket type
- `GET /ticket-types` - Get all ticket types
- `GET /ticket-types/{type_id}/bookings` - Get bookings for ticket type

### Bookings
- `POST /bookings` - Create new booking
- `GET /bookings` - Get all bookings with details
- `PUT /bookings/{booking_id}` - Update booking details
- `DELETE /bookings/{booking_id}` - Cancel booking
- `PATCH /bookings/{booking_id}/status` - Update booking status

### Advanced Queries
- `GET /bookings/search` - Search bookings by criteria
- `GET /booking-system/stats` - Get comprehensive statistics

## Database Schema

### Tables
1. **venues** - Venue information and capacity
2. **events** - Event details with venue relationships
3. **ticket_types** - Ticket pricing and descriptions
4. **bookings** - Customer bookings with relationships

### Relationships
- Events belong to Venues (foreign key: venue_id)
- Bookings belong to Events (foreign key: event_id)
- Bookings belong to Ticket Types (foreign key: ticket_type_id)

## Installation & Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the application**:
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Dependencies

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application
- **Jinja2**: Template engine for HTML rendering
- **python-multipart**: For handling form data

## UI Features

### Dashboard
- **Statistics Overview**: Total revenue, bookings, events, and venues
- **Booking Status Breakdown**: Visual representation of booking states
- **Tabbed Interface**: Easy navigation between different sections

### Event Management
- Add new events with venue selection
- View all events with booking counts
- Check event revenue and available tickets

### Venue Management
- Create venues with capacity limits
- Monitor venue occupancy rates
- Track events per venue

### Ticket Type Management
- Configure different ticket types with pricing
- Track bookings per ticket type
- Visual indicators for ticket type categories

### Booking Management
- Create bookings with validation
- Update booking status (confirm/cancel)
- View comprehensive booking details

### Search & Analytics
- Search bookings by multiple criteria
- Real-time availability checking
- Revenue and occupancy reporting

## Sample Data

The application initializes with sample data including:
- 3 venues (Madison Square Garden, Hollywood Bowl, Red Rocks Amphitheatre)
- 3 ticket types (VIP, Standard, Economy)
- 3 sample events
- 10 random bookings with various statuses

## Technical Highlights

- **Relationship Modeling**: Proper SQLAlchemy relationships with foreign keys
- **Data Validation**: Comprehensive Pydantic models for API validation
- **Error Handling**: Proper HTTP status codes and error messages
- **Business Logic**: Capacity enforcement and pricing calculations
- **Modern UI**: Responsive design with Tailwind CSS and Font Awesome icons
- **Real-time Updates**: Dynamic content updates without page reloads

## Database Relationships Demonstrated

1. **Foreign Key Constraints**: Prevents orphaned records
2. **Join Operations**: Efficient queries across related tables
3. **Cascade Behavior**: Proper handling of related data
4. **Capacity Management**: Business logic enforcement
5. **Revenue Calculations**: Aggregated queries across relationships
6. **Occupancy Tracking**: Complex calculations involving multiple tables

This system demonstrates a real-world application of database relationships in a ticket booking context, with proper validation, business logic, and user interface. 