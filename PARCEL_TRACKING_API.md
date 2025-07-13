# Parcel Tracking System API

A comprehensive FastAPI-based parcel tracking system using SQLModel and async operations.

## Features

- **Customer Management**: Unified customer model for both senders and receivers
- **Parcel Tracking**: Complete parcel lifecycle tracking with status updates
- **Station Management**: Manage shipping stations and hubs
- **Vehicle Management**: Track delivery vehicles
- **Delivery Staff Management**: Manage delivery personnel
- **Real-time Tracking**: Public API endpoint for parcel tracking

## API Endpoints

### Customers `/v1/customers`
- `GET /` - List all customers with filtering and pagination
- `GET /{customer_id}` - Get customer by ID
- `GET /email/{email}` - Get customer by email
- `POST /` - Create new customer
- `PUT /{customer_id}` - Update customer
- `PATCH /{customer_id}/activate` - Activate customer
- `PATCH /{customer_id}/deactivate` - Deactivate customer
- `DELETE /{customer_id}` - Delete customer

### Parcels `/v1/parcels`
- `GET /` - List all parcels with filtering
- `GET /{parcel_id}` - Get parcel by ID
- `GET /track/{tracking_number}` - Track parcel (public endpoint)
- `POST /` - Create new parcel (auto-generates tracking number)
- `PUT /{parcel_id}` - Update parcel
- `PATCH /{parcel_id}/status` - Update parcel status
- `PATCH /{parcel_id}/assign-vehicle` - Assign vehicle to parcel
- `PATCH /{parcel_id}/assign-delivery-staff` - Assign delivery staff
- `DELETE /{parcel_id}` - Delete parcel

### Stations `/v1/stations`
- `GET /` - List all stations with filtering
- `GET /{station_id}` - Get station by ID
- `GET /code/{station_code}` - Get station by code
- `POST /` - Create new station
- `PUT /{station_id}` - Update station
- `DELETE /{station_id}` - Delete station

### Vehicles `/v1/vehicles`
- `GET /` - List all vehicles with filtering
- `GET /{vehicle_id}` - Get vehicle by ID
- `GET /license/{license_plate}` - Get vehicle by license plate
- `POST /` - Create new vehicle
- `PUT /{vehicle_id}` - Update vehicle
- `DELETE /{vehicle_id}` - Delete vehicle

### Delivery Staff `/v1/delivery-staff`
- `GET /` - List all delivery staff
- `GET /{staff_id}` - Get staff by ID
- `GET /employee/{employee_id}` - Get staff by employee ID
- `POST /` - Create new delivery staff
- `PUT /{staff_id}` - Update delivery staff
- `DELETE /{staff_id}` - Delete delivery staff

## Models

### Customer
Unified model for both senders and receivers:
- `id`, `name`, `email`, `phone`, `address`, `is_active`
- Relationships: `sent_parcels`, `received_parcels`

### Parcel
Main entity for tracking packages:
- `tracking_number` (auto-generated), `weight`, `dimensions`, `service_price`
- `status` (created, picked_up, in_transit, etc.)
- Foreign keys: `sender_id`, `receiver_id`, `origin_station_id`, `destination_station_id`, `vehicle_id`, `delivery_staff_id`

### Station
Shipping hubs and centers:
- `name`, `code`, `address`, `city`, `state`, `postal_code`
- Relationships: `parcels_sent`, `parcels_received`

### Vehicle
Delivery vehicles:
- `license_plate`, `type`, `capacity`, `is_active`
- Relationship: `parcels`

### DeliveryStaff
Delivery personnel:
- `name`, `email`, `phone`, `employee_id`, `is_active`
- Relationship: `parcels`

## Parcel Status Flow

1. **CREATED** - Parcel is created in the system
2. **PICKED_UP** - Parcel has been collected from sender
3. **IN_TRANSIT** - Parcel is being transported
4. **AT_DESTINATION** - Parcel has arrived at destination station
5. **OUT_FOR_DELIVERY** - Parcel is out for final delivery
6. **DELIVERED** - Parcel has been successfully delivered
7. **FAILED_DELIVERY** - Delivery attempt failed
8. **RETURNED** - Parcel is being returned to sender

## Running the Application

```bash
# Install dependencies
poetry install

# Run development server
poetry run fastapi dev flasx/main.py

# Or use the script
./scripts/run-api-dev
```

## Database

The application uses SQLite with async support via aiosqlite. The database is automatically created and tables are set up on application startup.

## Architecture

- **FastAPI** for the web framework
- **SQLModel** for database models and validation
- **Asyncio** for asynchronous operations
- **Pydantic** for data validation and serialization
- **SQLAlchemy** (via SQLModel) for ORM functionality
