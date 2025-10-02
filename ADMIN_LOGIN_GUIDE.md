# Admin Login Guide

This guide explains how to use the admin login functionality in the 33 Koti Dham API.

## Features Added

✅ **Admin Login with Password** - Admins can login using mobile/email and password  
✅ **Role-based Access Control** - Separate admin and super admin roles  
✅ **Admin Creation** - Super admins can create new admin users  
✅ **Initial Setup** - Easy setup for the first super admin  

## API Endpoints

### 1. Setup First Super Admin
**POST** `/api/v1/auth/setup-super-admin`

Creates the first super admin account. This endpoint only works if no super admin exists.

```json
{
  "name": "Super Admin",
  "email": "admin@33kotidham.com",
  "mobile": "9999999999",
  "password": "admin123",
  "role": "super_admin"
}
```

### 2. Admin Login
**POST** `/api/v1/auth/admin-login`

Login with admin credentials using mobile or email as username.

```json
{
  "username": "9999999999",  // Can be mobile or email
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create New Admin (Super Admin Only)
**POST** `/api/v1/auth/create-admin`

Super admins can create new admin users.

**Headers:**
```
Authorization: Bearer <super_admin_token>
```

**Body:**
```json
{
  "name": "Admin User",
  "email": "admin2@33kotidham.com",
  "mobile": "8888888888",
  "password": "admin456",
  "role": "admin"
}
```

## User Roles

- **`user`** - Regular users (default)
- **`admin`** - Admin users with elevated permissions
- **`super_admin`** - Super admins with full access

## Security Features

1. **Password Hashing** - All passwords are securely hashed using bcrypt
2. **Role Verification** - Admin endpoints verify user roles
3. **JWT Tokens** - Secure token-based authentication
4. **Input Validation** - All inputs are validated using Pydantic schemas

## Usage Examples

### 1. Initial Setup
```bash
# Create the first super admin
curl -X POST "http://localhost:8000/api/v1/auth/setup-super-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Super Admin",
    "email": "admin@33kotidham.com", 
    "mobile": "9999999999",
    "password": "admin123"
  }'
```

### 2. Admin Login
```bash
# Login with mobile
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "9999999999",
    "password": "admin123"
  }'

# Login with email
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@33kotidham.com",
    "password": "admin123"
  }'
```

### 3. Create New Admin
```bash
# Get token first, then create admin
curl -X POST "http://localhost:8000/api/v1/auth/create-admin" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_super_admin_token>" \
  -d '{
    "name": "New Admin",
    "email": "newadmin@33kotidham.com",
    "mobile": "8888888888", 
    "password": "newadmin123",
    "role": "admin"
  }'
```

## Testing

Run the test script to verify functionality:

```bash
python test_admin_login.py
```

This will test:
- Super admin creation
- Admin login with mobile and email
- Invalid login rejection
- Token validation
- Access control

## Error Handling

Common error responses:

- **401 Unauthorized** - Invalid credentials
- **403 Forbidden** - Insufficient permissions (not admin)
- **400 Bad Request** - User already exists or validation errors
- **500 Internal Server Error** - Server issues

## Integration with Existing System

The admin login system integrates seamlessly with:

- ✅ Existing user authentication
- ✅ JWT token system
- ✅ Role-based access control
- ✅ Database models
- ✅ FastAPI documentation

## Next Steps

You can now:

1. **Setup your first super admin** using `/setup-super-admin`
2. **Login as admin** using `/admin-login`
3. **Create additional admins** using `/create-admin`
4. **Use admin tokens** to access protected admin endpoints
5. **Integrate with frontend** admin panels

The admin system is ready for production use with proper security measures in place!
