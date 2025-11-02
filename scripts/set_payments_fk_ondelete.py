"""Script to alter the payments.booking_id foreign key to ON DELETE CASCADE.

This will modify the database constraint so that when a Booking is deleted,
its related Payment rows are deleted automatically by the database.

Run this against your production or development DB carefully. It executes raw
ALTER TABLE statements. Make a DB backup before running in production.
"""
import os
import sys
from sqlalchemy import text
# Ensure project root is on sys.path when script executed directly so `import app` works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine


SQL = '''
BEGIN;
-- Drop existing constraint if present (Postgres syntax)
ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_booking_id_fkey;
-- Recreate constraint with ON DELETE CASCADE
ALTER TABLE payments ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE;
COMMIT;
'''


def main():
    with engine.connect() as conn:
        try:
            print("Altering payments.booking_id foreign key to ON DELETE CASCADE...")
            conn.execute(text(SQL))
            print("Constraint updated successfully.")
        except Exception as e:
            print("Failed to update constraint:", e)


if __name__ == "__main__":
    main()
