# Product Order System with Payment Integration

## Changes Made:

### 1. **Database Models Updated** (`app/models.py`)
- Added `allow_cod` field to `Product` model (Cash on Delivery support per product)
- Added `payment_method` field to `Order` model (online/cod)

### 2. **Database Migration**
- Created migration: `af96049e7c18_add_payment_methods_to_product_and_order.py`
- Successfully applied to database

### 3. **Schemas Updated** (`app/schemas.py`)
- Added `allow_cod` field to Product schemas
- Added `payment_method` validation to OrderCreate schema
- Updated OrderResponse to include `payment_method`

### 4. **API Endpoints**

#### **Products API** (`/api/v1/products`)
- Products now have `allow_cod` flag (admin can enable/disable COD per product)
- When creating/updating products, admin can set which products support COD

#### **Orders API** (`/api/v1/orders`)
- **POST /orders** - Create order with payment method selection
  - Validates if all products in cart support COD when COD is selected
  - Prevents COD selection if any product doesn't allow it
  - Payment methods: `"online"` or `"cod"`

#### **Payment Integration** (`/api/v1/order-payments`)
New endpoints for Razorpay integration:

1. **POST /order-payments/create-razorpay-order**
   - Creates Razorpay order for online payment
   - Only works for orders with `payment_method: "online"`
   - Returns Razorpay order ID and key for frontend integration

2. **POST /order-payments/verify-payment**
   - Verifies Razorpay payment signature
   - Updates order status to "confirmed" on successful payment
   - Restores stock if payment fails

3. **GET /order-payments/{order_id}/payment-status**
   - Check payment status of an order
   - Returns complete payment details

## Order Flow:

### **For Online Payment:**
1. User creates order with `payment_method: "online"`
2. Frontend calls `/create-razorpay-order` to get Razorpay order details
3. User completes payment on Razorpay
4. Frontend calls `/verify-payment` with payment details
5. System verifies signature and confirms order

### **For Cash on Delivery:**
1. User creates order with `payment_method: "cod"`
2. System validates all products support COD
3. Order is created with status "pending"
4. Admin manually confirms order when payment is received
5. Admin updates order status via `/orders/{id}` endpoint

## Payment Status Flow:
- **Online Payment:**
  - Created → Pending → Success/Failed
  - Order status: pending → confirmed (on payment success)

- **Cash on Delivery:**
  - Order created with payment_status: "pending"
  - Admin confirms manually when cash is received
  - Admin updates via PUT `/orders/{id}` endpoint

## Admin Controls:
- Set `allow_cod: true` for products that support COD
- Manage orders and update payment status
- Track all orders via `/orders/all` endpoint

## Example Usage:

### Create Product with COD Support:
```json
{
  "name": "Rudraksha Mala",
  "slug": "rudraksha-mala",
  "mrp": 500,
  "selling_price": 450,
  "allow_cod": true,
  "stock_quantity": 100
}
```

### Create Order with COD:
```json
{
  "items": [{"product_id": 1, "quantity": 2}],
  "payment_method": "cod",
  "shipping_name": "John Doe",
  "shipping_mobile": "9876543210",
  "shipping_address": "123 Main St",
  "shipping_city": "Mumbai",
  "shipping_state": "Maharashtra",
  "shipping_pincode": "400001"
}
```

### Create Order with Online Payment:
```json
{
  "items": [{"product_id": 1, "quantity": 2}],
  "payment_method": "online",
  ...shipping details...
}
```
Then call `/create-razorpay-order` to initiate payment.

## Notes:
- COD validation happens at order creation
- If any product in cart doesn't support COD, the entire order must use online payment
- Razorpay integration requires valid RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in settings
- Stock is automatically managed (reduced on order, restored on failed payment)
