from app.database import SessionLocal
from app.models import Product

db = SessionLocal()

# Check product id 5
product = db.query(Product).filter(Product.id == 5).first()

if product:
    print(f"Product: {product.name}")
    print(f"Selling Price: ₹{product.selling_price}")
    print(f"Shipping Charge: ₹{product.shipping_charge}")
    print(f"Free Shipping Above: ₹{product.free_shipping_above}")
else:
    print("Product not found")

db.close()
