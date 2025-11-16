from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional, Annotated, Iterator
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import time
import random

# --- 1. Database Configuration (SQLAlchemy with SQLite) ---

# We'll use a local SQLite file for simplicity and persistence
SQLALCHEMY_DATABASE_URL = "sqlite:///./netsuite_mock.db"

# engine is the entry point to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite when using FastAPI
)

# SessionLocal is the class used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the ORM models
Base = declarative_base()

# Dependency to get a DB session for each request
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. SQLAlchemy ORM Models (Database Tables) ---

class DBCustomer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    entityId = Column(String, index=True, unique=True)
    companyName = Column(String)
    email = Column(String)
    status = Column(String)
    dateCreated = Column(String)
    lastUpdated = Column(String, nullable=True)

class DBSalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    tranId = Column(String, index=True, unique=True)
    entity = Column(Integer)  # Foreign key reference to customer.id (internal ID)
    total = Column(Float)
    status = Column(String)
    trandate = Column(String)
    lastUpdated = Column(String, nullable=True)

# Create tables in the database file (if they don't exist)
Base.metadata.create_all(bind=engine)

# --- 3. Pydantic Schemas (API Data Structure) ---

class CustomerBase(BaseModel):
    """Base schema for creating a Customer (no ID needed)."""
    companyName: str
    email: str
    status: str = "Active"

class CustomerResponse(CustomerBase):
    """Response schema including DB-generated fields."""
    id: int
    entityId: str
    dateCreated: str
    lastUpdated: Optional[str] = None
    
    class Config:
        from_attributes = True # Enable ORM mode for SQLAlchemy

class SalesOrderBase(BaseModel):
    """Base schema for creating a Sales Order."""
    entity: int  # Internal ID of the Customer
    total: float
    status: str = "Pending Fulfillment"
    trandate: Optional[str] = None

class SalesOrderResponse(SalesOrderBase):
    """Response schema including DB-generated fields."""
    id: int
    tranId: str
    lastUpdated: Optional[str] = None
    
    class Config:
        from_attributes = True # Enable ORM mode for SQLAlchemy

# --- 4. FastAPI Application Setup ---

app = FastAPI(
    title="GetSuite: Mock NetSuite API",
    description="A persistent mock server simulating NetSuite SuiteTalk REST Web Services.",
    version="v1"
)

# --- 5. Utility for simulating network latency ---
def simulate_latency():
    """Pauses execution for a realistic, random delay (50ms to 300ms)."""
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)

# --- 6. API Endpoints (Using DB Session) ---

# --- Customer Endpoints ---

@app.post("/services/rest/record/v1/customer", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, tags=["Customer"])
def create_customer(customer: CustomerBase, db: Annotated[Session, Depends(get_db)]):
    """Creates a new Customer record."""
    simulate_latency()
    
    # 1. Create a dummy model instance to save
    db_customer = DBCustomer(
        **customer.model_dump(),
        dateCreated=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        entityId="" # Temporarily empty
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    # 2. Update the entityId using the final database ID (a Netsuite pattern)
    db_customer.entityId = f"CUST-{db_customer.id}"
    db.commit()
    db.refresh(db_customer)
    
    return db_customer

@app.get("/services/rest/record/v1/customer", response_model=List[CustomerResponse], tags=["Customer"])
def get_customer_collection(db: Annotated[Session, Depends(get_db)]):
    """Retrieves a collection of Customer records."""
    simulate_latency()
    customers = db.query(DBCustomer).all()
    return customers

@app.get("/services/rest/record/v1/customer/{customer_id}", response_model=CustomerResponse, tags=["Customer"])
def get_customer_by_id(customer_id: int, db: Annotated[Session, Depends(get_db)]):
    """Retrieves a single Customer record by internal ID."""
    simulate_latency()
    customer = db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/services/rest/record/v1/customer/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customer"])
def update_customer(customer_id: int, customer_update: CustomerBase, db: Annotated[Session, Depends(get_db)]):
    """Updates an existing Customer record by internal ID (simulates status change)."""
    simulate_latency()
    customer = db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Simulate a specific status update
    customer.status = "On Hold"
    customer.lastUpdated = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Apply updates from the payload
    for key, value in customer_update.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
        
    db.commit()
    return 

@app.delete("/services/rest/record/v1/customer/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customer"])
def delete_customer(customer_id: int, db: Annotated[Session, Depends(get_db)]):
    """Deletes a Customer record by internal ID."""
    simulate_latency()
    customer = db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return

# --- Sales Order Endpoints ---

@app.post("/services/rest/record/v1/salesorder", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED, tags=["Sales Order"])
def create_sales_order(order: SalesOrderBase, db: Annotated[Session, Depends(get_db)]):
    """Creates a new Sales Order record."""
    simulate_latency()
    
    # Check if the referenced customer entity exists
    customer = db.query(DBCustomer).filter(DBCustomer.id == order.entity).first()
    if not customer:
        raise HTTPException(status_code=400, detail=f"Customer ID {order.entity} not found. Cannot create Sales Order.")

    db_order = DBSalesOrder(
        **order.model_dump(),
        trandate=order.trandate or time.strftime("%Y-%m-%d")
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # In a real Netsuite mock, we might set tranId here using db_order.id
    db_order.tranId = f"SO-{db_order.id}"
    db.commit()
    db.refresh(db_order)
    
    return db_order

@app.put("/services/rest/record/v1/salesorder/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Sales Order"])
def update_sales_order(order_id: int, order_update: SalesOrderBase, db: Annotated[Session, Depends(get_db)]):
    """Updates an existing Sales Order record by internal ID (simulates billing)."""
    simulate_latency()
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales Order not found")
    
    # Simulate the update of the order status to "Billed"
    order.status = "Billed"
    order.lastUpdated = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    db.commit()
    return 

@app.delete("/services/rest/record/v1/salesorder/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Sales Order"])
def delete_sales_order(order_id: int, db: Annotated[Session, Depends(get_db)]):
    """Deletes a Sales Order record by internal ID."""
    simulate_latency()
    order = db.query(DBSalesOrder).filter(DBSalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales Order not found")
        
    db.delete(order)
    db.commit()
    return