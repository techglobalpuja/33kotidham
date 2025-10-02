#!/usr/bin/env python3
"""
Test script to verify the updated Puja model works correctly
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud
from datetime import date, time

def test_puja_model():
    """Test the updated Puja model with all new fields."""
    db: Session = SessionLocal()
    
    try:
        print("Testing updated Puja model...")
        
        # Create a test puja with all new fields
        puja_data = schemas.PujaCreate(
            name="Ganga Aarti",
            sub_heading="Divine River Worship Ceremony",
            description="A sacred evening ritual performed on the banks of River Ganga",
            date=date(2024, 12, 25),
            time=time(18, 30),
            
            # Temple details
            temple_image_url="https://example.com/temple.jpg",
            temple_address="Dashashwamedh Ghat, Varanasi, Uttar Pradesh, India",
            temple_description="Ancient ghat on the holy Ganges river",
            
            # Prasad
            prasad_price=251,
            is_prasad_active=True,
            
            # Dakshina
            dakshina_prices_inr="101,251,501,1001",
            dakshina_prices_usd="2,5,10,20",
            is_dakshina_active=True,
            
            # Manokamna
            manokamna_prices_inr="251,501,1001,2001",
            manokamna_prices_usd="5,10,20,40",
            is_manokamna_active=True,
            
            # General
            category="Evening Aarti"
        )
        
        # Create puja
        puja = crud.PujaCRUD.create_puja(db, puja_data)
        print(f"✓ Created puja: {puja.name}")
        print(f"  Sub-heading: {puja.sub_heading}")
        print(f"  Date & Time: {puja.date} at {puja.time}")
        print(f"  Temple: {puja.temple_address}")
        print(f"  Prasad Active: {puja.is_prasad_active} (₹{puja.prasad_price})")
        print(f"  Dakshina Active: {puja.is_dakshina_active}")
        print(f"  Manokamna Active: {puja.is_manokamna_active}")
        print(f"  Category: {puja.category}")
        
        # Add benefits
        benefits = [
            "Brings peace and prosperity to family",
            "Removes negative energies from home",
            "Fulfills wishes and desires",
            "Provides spiritual purification"
        ]
        
        for benefit_text in benefits:
            benefit_data = schemas.PujaBenefitCreate(
                puja_id=puja.id,
                benefit_text=benefit_text
            )
            benefit = crud.PujaBenefitCRUD.create_puja_benefit(db, benefit_data)
            print(f"  ✓ Added benefit: {benefit.benefit_text}")
        
        # Retrieve puja with benefits
        retrieved_puja = crud.PujaCRUD.get_puja(db, puja.id)
        puja_benefits = crud.PujaBenefitCRUD.get_puja_benefits(db, puja.id)
        
        print(f"\n✓ Retrieved puja with {len(puja_benefits)} benefits")
        
        # Clean up
        crud.PujaCRUD.delete_puja(db, puja.id)
        print(f"✓ Cleaned up test puja")
        
        print("\n🎉 All tests passed! Updated Puja model is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_puja_model()
