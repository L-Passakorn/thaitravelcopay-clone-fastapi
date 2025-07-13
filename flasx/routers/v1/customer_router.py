from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from flasx.schemas import customer_schema
from flasx.models import get_session, Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get(
    "",
    summary="Get all customers",
    description="Retrieve a list of all customers with optional filtering.",
    response_model=list[customer_schema.Customer],
)
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> list[customer_schema.Customer]:
    """Get all customers with optional pagination and filtering."""
    query = select(Customer)

    # Apply filters
    if is_active is not None:
        query = query.where(Customer.is_active == is_active)
    if search:
        query = query.where(
            (Customer.name.ilike(f"%{search}%")) | (Customer.email.ilike(f"%{search}%"))
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    customers = result.all()

    return [customer_schema.Customer.model_validate(customer) for customer in customers]


@router.get(
    "/{customer_id}",
    summary="Get a customer by ID",
    description="Retrieve a specific customer using their unique identifier.",
    response_model=customer_schema.Customer,
)
async def get_customer(
    customer_id: int, session: AsyncSession = Depends(get_session)
) -> customer_schema.Customer:
    """Get a single customer by ID."""
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer_schema.Customer.model_validate(customer)


@router.get(
    "/email/{email}",
    summary="Get a customer by email",
    description="Retrieve a specific customer using their email address.",
    response_model=customer_schema.Customer,
)
async def get_customer_by_email(
    email: str, session: AsyncSession = Depends(get_session)
) -> customer_schema.Customer:
    """Get a single customer by email."""
    query = select(Customer).where(Customer.email == email)
    result = await session.exec(query)
    customer = result.first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer_schema.Customer.model_validate(customer)


@router.post(
    "",
    summary="Create a new customer",
    description="Create a new customer with the provided details.",
    response_model=customer_schema.Customer,
    status_code=201,
)
async def create_customer(
    customer: customer_schema.CustomerCreate,
    session: AsyncSession = Depends(get_session),
) -> customer_schema.Customer:
    """Create a new customer."""
    # Check if email already exists
    print("check session", type(session))
    query = select(Customer).where(Customer.email == customer.email)
    result = await session.exec(query)
    existing_customer = result.first()

    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new customer
    db_customer = Customer(**customer.model_dump())
    session.add(db_customer)
    await session.commit()
    await session.refresh(db_customer)

    return customer_schema.Customer.model_validate(db_customer)


@router.put(
    "/{customer_id}",
    summary="Update an existing customer",
    description="Update an existing customer with the provided details.",
    response_model=customer_schema.Customer,
)
async def update_customer(
    customer_id: int,
    customer_update: customer_schema.CustomerUpdate,
    session: AsyncSession = Depends(get_session),
) -> customer_schema.Customer:
    """Update an existing customer."""
    db_customer = await session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if email is being updated and already exists
    if customer_update.email:
        query = select(Customer).where(
            Customer.email == customer_update.email, Customer.id != customer_id
        )
        result = await session.exec(query)
        existing_customer = result.first()

        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Update only provided fields
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    # Update timestamp
    db_customer.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_customer)

    return customer_schema.Customer.model_validate(db_customer)


@router.patch(
    "/{customer_id}/activate",
    summary="Activate a customer",
    description="Activate a customer by setting is_active to True.",
    response_model=customer_schema.Customer,
)
async def activate_customer(
    customer_id: int, session: AsyncSession = Depends(get_session)
) -> customer_schema.Customer:
    """Activate a customer."""
    db_customer = await session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_customer.is_active = True
    db_customer.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_customer)

    return customer_schema.Customer.model_validate(db_customer)


@router.patch(
    "/{customer_id}/deactivate",
    summary="Deactivate a customer",
    description="Deactivate a customer by setting is_active to False.",
    response_model=customer_schema.Customer,
)
async def deactivate_customer(
    customer_id: int, session: AsyncSession = Depends(get_session)
) -> customer_schema.Customer:
    """Deactivate a customer."""
    db_customer = await session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_customer.is_active = False
    db_customer.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_customer)

    return customer_schema.Customer.model_validate(db_customer)


@router.delete(
    "/{customer_id}",
    summary="Delete a customer",
    description="Delete a customer by ID.",
    status_code=204,
)
async def delete_customer(
    customer_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete a customer."""
    db_customer = await session.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    await session.delete(db_customer)
    await session.commit()
    return None
