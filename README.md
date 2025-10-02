# 33 Koti Dham API

A FastAPI backend for an online platform that allows users to book Puja with prasad and chadawa.

## Features

- **User Management**: Three user roles (Super Admin, Admin, User)
- **Authentication**: JWT-based authentication with OTP login support
- **Puja Management**: Create and manage different pujas
- **Plan Management**: Multiple pricing plans for pujas
- **Chadawa Management**: Manage prasad and offerings
- **Booking System**: Complete booking workflow
- **Payment Integration**: Razorpay payment gateway integration
- **File Upload**: Image upload for pujas and plans
- **Admin Dashboard**: Statistics and management interface
- **Notifications**: SMS and Email notifications

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Alembic**: Database migration tool
- **Razorpay**: Payment gateway
- **Twilio**: SMS service
- **JWT**: Authentication tokens
- **Pydantic**: Data validation

## Project Structure

```
33kotidham/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── auth.py              # Authentication utilities
│   ├── utils.py             # Utility functions
│   ├── services.py          # External services (SMS, Email)
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── auth.py          # Authentication routes
│       ├── users.py         # User management
│       ├── pujas.py         # Puja management
│       ├── plans.py         # Plan management
│       ├── chadawas.py      # Chadawa management
│       ├── bookings.py      # Booking system
│       ├── payments.py      # Payment handling
│       ├── admin.py         # Admin dashboard
│       └── uploads.py       # File uploads
├── alembic/                 # Database migrations
├── uploads/                 # Uploaded files
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd 33kotidham
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Update the following variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/33kotidham_db

# JWT
SECRET_KEY=your-secret-key-here

# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Email
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE 33kotidham_db;
```

Initialize Alembic and create tables:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Create Super Admin User

Run the application and use the registration endpoint to create a super admin:

```bash
python -m app.main
```

Then make a POST request to `/api/v1/auth/register` with:

```json
{
  "name": "Super Admin",
  "email": "admin@33kotidham.com",
  "mobile": "+919999999999",
  "password": "securepassword",
  "role": "super_admin"
}
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with password
- `POST /api/v1/auth/request-otp` - Request OTP
- `POST /api/v1/auth/verify-otp` - Verify OTP and login
- `GET /api/v1/auth/me` - Get current user info

### User Management
- `GET /api/v1/users/` - Get all users (Admin)
- `POST /api/v1/users/` - Create user (Admin)
- `GET /api/v1/users/{id}` - Get user by ID (Admin)
- `PUT /api/v1/users/{id}` - Update user (Admin)
- `DELETE /api/v1/users/{id}` - Delete user (Super Admin)

### Pujas
- `GET /api/v1/pujas/` - Get all pujas
- `POST /api/v1/pujas/` - Create puja (Admin)
- `GET /api/v1/pujas/{id}` - Get puja by ID
- `PUT /api/v1/pujas/{id}` - Update puja (Admin)
- `DELETE /api/v1/pujas/{id}` - Delete puja (Admin)

### Plans
- `GET /api/v1/plans/` - Get all plans
- `POST /api/v1/plans/` - Create plan (Admin)
- `GET /api/v1/plans/{id}` - Get plan by ID
- `PUT /api/v1/plans/{id}` - Update plan (Admin)
- `DELETE /api/v1/plans/{id}` - Delete plan (Admin)

### Chadawas
- `GET /api/v1/chadawas/` - Get all chadawas
- `POST /api/v1/chadawas/` - Create chadawa (Admin)
- `GET /api/v1/chadawas/{id}` - Get chadawa by ID
- `PUT /api/v1/chadawas/{id}` - Update chadawa (Admin)
- `DELETE /api/v1/chadawas/{id}` - Delete chadawa (Admin)

### Bookings
- `GET /api/v1/bookings/` - Get bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/{id}` - Get booking by ID
- `PUT /api/v1/bookings/{id}` - Update booking (Admin)
- `PUT /api/v1/bookings/{id}/cancel` - Cancel booking
- `PUT /api/v1/bookings/{id}/confirm` - Confirm booking (Admin)
- `PUT /api/v1/bookings/{id}/complete` - Complete booking (Admin)

### Payments
- `POST /api/v1/payments/create-order` - Create payment order
- `POST /api/v1/payments/verify` - Verify payment
- `GET /api/v1/payments/{id}` - Get payment by ID
- `GET /api/v1/payments/booking/{booking_id}` - Get payment by booking
- `POST /api/v1/payments/{id}/refund` - Refund payment (Admin)

### Admin Dashboard
- `GET /api/v1/admin/dashboard` - Get dashboard stats
- `GET /api/v1/admin/bookings/pending` - Get pending bookings
- `GET /api/v1/admin/bookings/recent` - Get recent bookings
- `GET /api/v1/admin/revenue/monthly` - Get monthly revenue

### File Uploads
- `POST /api/v1/uploads/images` - Upload image (Admin)
- `POST /api/v1/uploads/puja-images/{puja_id}` - Upload puja image (Admin)
- `DELETE /api/v1/uploads/puja-images/{image_id}` - Delete puja image (Admin)

## User Roles

### Super Admin
- Full access to all features
- Can create/delete other admins
- Can delete users
- System configuration access

### Admin
- Manage pujas, plans, and chadawas
- Manage user bookings
- Process payments and refunds
- View dashboard and reports
- Upload files

### User
- Register and login
- Browse pujas and plans
- Create bookings
- Make payments
- View own booking history

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Production Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Set up Nginx reverse proxy
4. Use Gunicorn or similar WSGI server
5. Set up SSL certificates
6. Configure monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
