# Expense Tracker - FastAPI with SQLite

A comprehensive expense tracking application built with FastAPI, SQLAlchemy, and SQLite. Track your expenses with categories, analytics, and advanced filtering capabilities.

## Features

### Core Features
- ✅ **Create, Read, Update, Delete (CRUD) expenses**
- ✅ **SQLite database with SQLAlchemy ORM**
- ✅ **Automatic database table creation**
- ✅ **Sample data initialization**
- ✅ **Beautiful responsive UI with Tailwind CSS**

### Advanced Features
- ✅ **Data Validation**: Positive amounts, predefined categories
- ✅ **Category Filtering**: Filter expenses by category
- ✅ **Date Range Filtering**: Filter by start and end dates
- ✅ **Total Expenses & Category Breakdown**
- ✅ **Analytics Dashboard**: Summary cards and visual breakdowns
- ✅ **Currency Formatting**: Proper $ formatting
- ✅ **Error Handling**: Comprehensive error handling with user feedback

### API Endpoints

#### Expense Management
- `GET /expenses` - Fetch all expenses (with optional date filtering)
- `POST /expenses` - Create a new expense
- `PUT /expenses/{expense_id}` - Update an existing expense
- `DELETE /expenses/{expense_id}` - Delete an expense

#### Analytics & Filtering
- `GET /expenses/category/{category}` - Filter expenses by category
- `GET /expenses/total` - Get total expenses and breakdown by category
- `GET /filter` - Web UI filtering with multiple parameters

#### Query Parameters
- `start_date` - Filter expenses from this date (YYYY-MM-DD)
- `end_date` - Filter expenses until this date (YYYY-MM-DD)
- `category` - Filter by specific category

### Categories
- Food
- Transport
- Entertainment
- Shopping
- Bills
- Healthcare
- Other

## Setup Instructions

### 1. Install Dependencies
```bash
cd q2
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

The application will:
- Create the SQLite database automatically
- Initialize sample data if none exists
- Start the server on http://localhost:8001

### 3. Access the Application
- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs (FastAPI auto-generated)
- **Alternative API Docs**: http://localhost:8001/redoc

## Database Schema

### ExpenseDB Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL
);
```

## API Usage Examples

### Create Expense
```bash
curl -X POST "http://localhost:8001/expenses" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "amount=25.50&category=Food&description=Lunch&date=2024-01-15"
```

### Get All Expenses
```bash
curl -X GET "http://localhost:8001/expenses"
```

### Get Expenses with Date Filter
```bash
curl -X GET "http://localhost:8001/expenses?start_date=2024-01-01&end_date=2024-01-31"
```

### Get Expenses by Category
```bash
curl -X GET "http://localhost:8001/expenses/category/Food"
```

### Get Total and Breakdown
```bash
curl -X GET "http://localhost:8001/expenses/total"
```

### Update Expense
```bash
curl -X PUT "http://localhost:8001/expenses/1" \
  -H "Content-Type: application/json" \
  -d '{"amount": 30.00, "category": "Food", "description": "Updated lunch", "date": "2024-01-15"}'
```

### Delete Expense
```bash
curl -X DELETE "http://localhost:8001/expenses/1"
```

## UI Features

### Dashboard
- **Summary Cards**: Total expenses, number of expenses, average expense
- **Category Breakdown**: Visual breakdown with progress bars
- **Analytics**: Real-time calculations

### Expense Management
- **Add Form**: Easy-to-use form with validation
- **Edit Modal**: In-place editing with modal dialog
- **Delete Confirmation**: Safe deletion with confirmation

### Filtering
- **Category Filter**: Dropdown with all categories
- **Date Range Filter**: Start and end date pickers
- **Combined Filtering**: Mix category and date filters

### Table Display
- **Responsive Table**: Works on mobile and desktop
- **Date Formatting**: User-friendly date display
- **Currency Formatting**: Proper $ formatting
- **Color-coded Categories**: Visual category identification

## Data Validation

### Amount Validation
- Must be a positive number (> 0)
- Supports decimal places (e.g., 25.50)
- Client-side and server-side validation

### Category Validation
- Must be from predefined list
- Server-side validation with error messages

### Date Validation
- Must be a valid date
- HTML5 date picker for easy input

## Error Handling

### API Errors
- 422: Validation errors (invalid data)
- 404: Expense not found
- 500: Server errors

### UI Error Handling
- Form validation before submission
- User-friendly error messages
- Confirmation dialogs for destructive actions

## Development Notes

### Database Setup
- Uses SQLAlchemy ORM for database operations
- SQLite database file: `expenses.db`
- Automatic table creation on startup
- Sample data initialization

### Session Management
- Proper database session handling
- Automatic session cleanup
- Error rollback on failures

### Architecture
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Jinja2**: Template engine for HTML rendering
- **Tailwind CSS**: Utility-first CSS framework

## File Structure
```
q2/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── expenses.db         # SQLite database (created automatically)
├── templates/
│   └── index.html      # Main UI template
└── static/             # Static files (empty - using CDN)
```

This expense tracker provides a solid foundation for personal finance management with room for future enhancements! 