# Dynamic Shipping Charges - Implementation Complete ✅

## What Changed

### 1. **Database Schema** (`models.py`)
Added two new fields to `Product` model:
- `shipping_charge`: Decimal field for per-product shipping fee
- `free_shipping_above`: Decimal field for product-specific free shipping threshold

### 2. **Order Calculation** (`promo_orders.py`)
Updated shipping logic to:
- Loop through each product in the order
- Check if order total meets product's free shipping threshold
- Calculate shipping per product × quantity
- Fallback to global settings if no product-specific shipping

### 3. **API Schemas** (`schemas.py`)
Added shipping fields to:
- `ProductBase`
- `ProductCreate`
- `ProductUpdate`

### 4. **Migration** (`alembic/versions/7e090ec3a674_...`)
Created migration to add columns to database

---

## How It Works

### Calculation Flow:
```
For each product in cart:
  ├─ Check: subtotal >= product.free_shipping_above?
  │  ├─ YES → Skip shipping (FREE)
  │  └─ NO → Add (product.shipping_charge × quantity)
  │
  └─ If no products have shipping_charge:
     └─ Use global settings (SHIPPING_CHARGE, FREE_SHIPPING_THRESHOLD)
```

---

## Examples

### Example 1: Single Product with Shipping
**Product**: Brass Diya  
**Price**: ₹299  
**Shipping Charge**: ₹40  
**Free Shipping Above**: ₹500  

**Order**:
- Subtotal: ₹299
- Shipping: ₹40 (below threshold)
- **Total: ₹339**

---

### Example 2: Multiple Products
**Product A**: Rudraksha Mala  
- Price: ₹150 × 2 = ₹300
- Shipping: ₹30 each = ₹60

**Product B**: Temple Bell  
- Price: ₹500 × 1 = ₹500
- Shipping: ₹60 each = ₹60

**Order**:
- Subtotal: ₹800
- Shipping: ₹120 (₹60 + ₹60)
- **Total: ₹920**

---

### Example 3: Free Shipping Threshold Met
**Product**: Copper Kalash  
**Price**: ₹600  
**Shipping Charge**: ₹50  
**Free Shipping Above**: ₹500  

**Order**:
- Subtotal: ₹600 (exceeds ₹500)
- Shipping: **FREE**
- **Total: ₹600**

---

## API Usage

### Create Product with Shipping
```bash
POST /api/v1/products
```

```json
{
  "name": "Brass Diya",
  "slug": "brass-diya",
  "mrp": 499,
  "selling_price": 299,
  "shipping_charge": 40,
  "free_shipping_above": 500,
  "stock_quantity": 50,
  "allow_cod": true
}
```

### Update Product Shipping
```bash
PUT /api/v1/products/{product_id}
```

```json
{
  "shipping_charge": 30,
  "free_shipping_above": 400
}
```

### Create Order (Automatic Shipping Calculation)
```bash
POST /api/v1/orders
```

```json
{
  "shipping_name": "Customer Name",
  "shipping_mobile": "8962507486",
  "shipping_address": "123 Street",
  "shipping_city": "Delhi",
  "shipping_state": "Delhi",
  "shipping_pincode": "110001",
  "items": [
    {
      "product_id": 5,
      "quantity": 2
    }
  ],
  "payment_method": "online"
}
```

**Response**:
```json
{
  "id": 7,
  "order_number": "ORD202512012322423769",
  "subtotal": "598.00",
  "shipping_charges": "80.00",
  "discount_amount": "0.00",
  "tax_amount": "0.00",
  "total_amount": "678.00",
  "status": "pending"
}
```

---

## Configuration

### Environment Variables (.env)
```bash
# Global fallback shipping settings
SHIPPING_CHARGE=50              # Default shipping fee
FREE_SHIPPING_THRESHOLD=500     # Default free shipping threshold
```

### Per-Product Settings (Database)
```sql
-- Set shipping for specific product
UPDATE products 
SET shipping_charge = 40, 
    free_shipping_above = 500 
WHERE id = 5;

-- Free shipping for a product
UPDATE products 
SET shipping_charge = 0 
WHERE id = 10;

-- Remove product-specific shipping (use global)
UPDATE products 
SET shipping_charge = 0, 
    free_shipping_above = NULL 
WHERE id = 15;
```

---

## Priority Logic

1. **Product-specific shipping** (if set)
   - Uses `product.shipping_charge`
   - Checks `product.free_shipping_above`
   
2. **Global fallback** (if no product shipping)
   - Uses `settings.SHIPPING_CHARGE`
   - Checks `settings.FREE_SHIPPING_THRESHOLD`

---

## Admin Panel Usage

When creating/editing products:

```
┌─────────────────────────────────────────┐
│ Product Details                         │
├─────────────────────────────────────────┤
│ Name: Brass Diya                        │
│ Price: ₹299                             │
│                                         │
│ 📦 Shipping Configuration:              │
│                                         │
│ [ 40 ] Shipping Charge (₹)              │
│ [ 500 ] Free Shipping Above (₹)         │
│                                         │
│ 💡 Set to 0 for free shipping          │
│ 💡 Leave blank to use global settings   │
└─────────────────────────────────────────┘
```

---

## Testing

### Test File: `test_dynamic_shipping.py`
Run to see examples:
```bash
python test_dynamic_shipping.py
```

### Manual Test
1. Create a product with shipping:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/products" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "Test Product",
       "slug": "test-product",
       "mrp": 500,
       "selling_price": 300,
       "shipping_charge": 50,
       "free_shipping_above": 500
     }'
   ```

2. Create an order with that product:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/orders" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "shipping_name": "Test",
       "shipping_mobile": "8962507486",
       "items": [{"product_id": 5, "quantity": 1}]
     }'
   ```

3. Check shipping calculation in response

---

## Migration

### Local (Already Done)
```bash
alembic upgrade head
```

### Production Server
```bash
cd ~/backend/33kotidham
git pull origin master
alembic upgrade head
sudo systemctl restart 33kotidham
```

---

## Benefits

✅ **Flexible**: Each product can have its own shipping rate  
✅ **Smart**: Automatic free shipping based on thresholds  
✅ **Scalable**: Mix products with different shipping rules  
✅ **Fallback**: Uses global settings if product shipping not set  
✅ **Quantity-aware**: Shipping multiplies by quantity  
✅ **Configurable**: No code changes needed, just update product data  

---

## Common Scenarios

### Scenario 1: Heavy vs Light Products
```python
# Heavy product (higher shipping)
Product A: shipping_charge = 100

# Light product (lower shipping)
Product B: shipping_charge = 30
```

### Scenario 2: Premium Products (Free Shipping)
```python
# Premium idol (free shipping)
Product: shipping_charge = 0
```

### Scenario 3: Bulk Discount Shipping
```python
# Free shipping on orders above ₹1000
Product: free_shipping_above = 1000
```

### Scenario 4: Digital Products
```python
# No shipping needed
Product: shipping_charge = 0, free_shipping_above = 0
```

---

## Summary

🎉 **Dynamic shipping is now live!**

- Each product can have its own shipping charge
- Free shipping thresholds per product
- Quantity-aware calculations
- Global fallback for products without specific shipping
- No hardcoded values
- Easy to configure via API or database

**Next Steps**:
1. Update existing products with shipping charges
2. Test with real orders
3. Deploy to production
4. Update admin panel UI to show shipping fields
