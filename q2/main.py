from fastapi import FastAPI, HTTPException, Request, Form, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./expenses.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ExpenseDB(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)

# Pydantic Models
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: date

    @field_validator('category')
    def validate_category(cls, v):
        valid_categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None

    @field_validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
            if v not in valid_categories:
                raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v

class Expense(ExpenseBase):
    id: int
    
    class Config:
        from_attributes = True

class ExpenseTotal(BaseModel):
    total: float
    breakdown: dict

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
app = FastAPI(title="Expense Tracker", description="Track your expenses with categories and analytics")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize sample data
def init_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_expenses = db.query(ExpenseDB).first()
        if existing_expenses:
            return
        
        # Add sample expenses
        sample_expenses = [
            ExpenseDB(amount=25.50, category="Food", description="Lunch at restaurant", date=date(2024, 1, 15)),
            ExpenseDB(amount=15.00, category="Transport", description="Bus fare", date=date(2024, 1, 16)),
            ExpenseDB(amount=89.99, category="Shopping", description="Groceries", date=date(2024, 1, 17)),
            ExpenseDB(amount=45.00, category="Entertainment", description="Movie tickets", date=date(2024, 1, 18)),
            ExpenseDB(amount=120.00, category="Bills", description="Internet bill", date=date(2024, 1, 19)),
            ExpenseDB(amount=75.00, category="Healthcare", description="Doctor visit", date=date(2024, 1, 20)),
        ]
        
        db.add_all(sample_expenses)
        db.commit()
        print("Sample data initialized!")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize sample data on startup
init_sample_data()

# API Endpoints
@app.get("/expenses", response_model=List[Expense])
async def get_expenses(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db)
):
    """Fetch all expenses with optional date range filtering"""
    query = db.query(ExpenseDB)
    
    if start_date:
        query = query.filter(ExpenseDB.date >= start_date)
    if end_date:
        query = query.filter(ExpenseDB.date <= end_date)
    
    expenses = query.order_by(ExpenseDB.date.desc()).all()
    return expenses

@app.post("/expenses", response_model=Expense, status_code=201)
async def create_expense(
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    expense_date: date = Form(..., alias="date"),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    try:
        # Validate the expense data
        expense_data = ExpenseCreate(
            amount=amount,
            category=category,
            description=description,
            date=expense_date
        )
        
        db_expense = ExpenseDB(**expense_data.dict())
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create expense")

@app.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    db_expense = db.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)
    
    try:
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update expense")

@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    db_expense = db.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    try:
        db.delete(db_expense)
        db.commit()
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete expense")

@app.get("/expenses/category/{category}", response_model=List[Expense])
async def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    """Filter expenses by category"""
    expenses = db.query(ExpenseDB).filter(ExpenseDB.category == category).order_by(ExpenseDB.date.desc()).all()
    return expenses

@app.get("/expenses/total", response_model=ExpenseTotal)
async def get_total_expenses(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db)
):
    """Get total expenses and breakdown by category"""
    query = db.query(ExpenseDB)
    
    if start_date:
        query = query.filter(ExpenseDB.date >= start_date)
    if end_date:
        query = query.filter(ExpenseDB.date <= end_date)
    
    # Calculate total
    total = query.with_entities(func.sum(ExpenseDB.amount)).scalar() or 0.0
    
    # Calculate breakdown by category
    breakdown_query = query.with_entities(
        ExpenseDB.category,
        func.sum(ExpenseDB.amount).label('total')
    ).group_by(ExpenseDB.category).all()
    
    breakdown = {category: float(total) for category, total in breakdown_query}
    
    return ExpenseTotal(total=float(total), breakdown=breakdown)

# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Main page with expense form and list"""
    expenses = db.query(ExpenseDB).order_by(ExpenseDB.date.desc()).all()
    
    # Get total and breakdown
    total = db.query(func.sum(ExpenseDB.amount)).scalar() or 0.0
    breakdown_query = db.query(
        ExpenseDB.category,
        func.sum(ExpenseDB.amount).label('total')
    ).group_by(ExpenseDB.category).all()
    breakdown = {category: float(total) for category, total in breakdown_query}
    
    categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "expenses": expenses,
            "total": float(total),
            "breakdown": breakdown,
            "categories": categories
        }
    )

@app.get("/filter", response_class=HTMLResponse)
async def filter_expenses(
    request: Request,
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Filter expenses by category and date range"""
    query = db.query(ExpenseDB)
    
    if category:
        query = query.filter(ExpenseDB.category == category)
    if start_date:
        query = query.filter(ExpenseDB.date >= start_date)
    if end_date:
        query = query.filter(ExpenseDB.date <= end_date)
    
    expenses = query.order_by(ExpenseDB.date.desc()).all()
    
    # Calculate filtered total and breakdown
    total = query.with_entities(func.sum(ExpenseDB.amount)).scalar() or 0.0
    breakdown_query = query.with_entities(
        ExpenseDB.category,
        func.sum(ExpenseDB.amount).label('total')
    ).group_by(ExpenseDB.category).all()
    breakdown = {category: float(total) for category, total in breakdown_query}
    
    categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "expenses": expenses,
            "total": float(total),
            "breakdown": breakdown,
            "categories": categories,
            "selected_category": category,
            "start_date": start_date,
            "end_date": end_date
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 