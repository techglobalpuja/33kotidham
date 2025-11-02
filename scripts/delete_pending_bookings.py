"""Utility script to delete pending bookings.

Usage:
  python scripts/delete_pending_bookings.py --days 30 [--dry-run]

Options:
  --days N     Delete pending bookings older than N days. Use 0 to delete ALL pending bookings (dangerous).
  --dry-run    Print how many would be deleted without performing deletion.
  --yes        Required when --days 0 to actually perform delete-all.

This script will also delete related payments (if any) before deleting bookings to
avoid foreign-key constraint issues. If your DB has ON DELETE CASCADE on payments.booking_id
the payments will be removed automatically.
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
# Ensure project root is on sys.path when script executed directly so `import app` works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app import models


def parse_args():
    p = argparse.ArgumentParser(description="Delete pending bookings script")
    p.add_argument("--days", type=int, default=30, help="Delete pending bookings older than DAYS. Use 0 to delete all pending bookings.")
    p.add_argument("--dry-run", action="store_true", help="Don't delete, just show counts")
    p.add_argument("--yes", action="store_true", help="Confirm destructive actions (required when --days 0)")
    p.add_argument("--before", type=str, default=None, help="Only consider bookings before this date (YYYY-MM-DD)")
    p.add_argument("--after", type=str, default=None, help="Only consider bookings after this date (YYYY-MM-DD)")
    p.add_argument("--list", action="store_true", help="List sample matching bookings (id, booking_date, mobile_number)")
    p.add_argument("--limit", type=int, default=100, help="Limit number of listed rows when --list is used")
    return p.parse_args()


def main():
    args = parse_args()
    days = args.days
    dry_run = args.dry_run
    before = args.before
    after = args.after
    do_list = args.list
    limit = args.limit

    db = SessionLocal()
    try:
        query = db.query(models.Booking).filter(models.Booking.status == models.BookingStatus.PENDING.value)

        # Apply filters: --days (older than), or explicit --before/--after dates (YYYY-MM-DD)
        if before or after:
            # parse dates if provided (support YYYY-MM-DD or full ISO datetime)
            if before:
                if len(before) == 10:
                    before_dt = datetime.fromisoformat(before + "T00:00:00").replace(tzinfo=timezone.utc)
                else:
                    before_dt = datetime.fromisoformat(before).replace(tzinfo=timezone.utc)
                query = query.filter(models.Booking.booking_date < before_dt)
            if after:
                if len(after) == 10:
                    after_dt = datetime.fromisoformat(after + "T00:00:00").replace(tzinfo=timezone.utc)
                else:
                    after_dt = datetime.fromisoformat(after).replace(tzinfo=timezone.utc)
                query = query.filter(models.Booking.booking_date > after_dt)
        else:
            if days > 0:
                # Use timezone-aware UTC datetime to avoid DeprecationWarning
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                query = query.filter(models.Booking.booking_date < cutoff)

        # Fetch matching booking ids and optionally sample rows
        rows = query.order_by(models.Booking.booking_date).all()
        booking_ids = [r.id for r in rows]
        count = len(booking_ids)

        if count == 0:
            print("No pending bookings matched the criteria.")
            return

        print(f"Pending bookings matched: {count}")

        if do_list:
            print(f"Listing up to {limit} matching pending bookings:")
            for r in rows[:limit]:
                print(f"id={r.id}\tbooking_date={r.booking_date}\tmobile={r.mobile_number}\tstatus={r.status}\tcreated_at={r.created_at}")
            print("")

        if dry_run:
            print("Dry-run mode, no deletions performed.")
            return

        if days == 0 and not args.yes:
            print("Refusing to delete ALL pending bookings without --yes. Re-run with --yes to confirm.")
            return

        # Delete payments referencing these bookings first (to be safe if DB FK is restrictive)
        payments_deleted = 0
        if booking_ids:
            payments_deleted = db.query(models.Payment).filter(models.Payment.booking_id.in_(booking_ids)).delete(synchronize_session=False)
            print(f"Payments deleted: {payments_deleted}")

            bookings_deleted = db.query(models.Booking).filter(models.Booking.id.in_(booking_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"Bookings deleted: {bookings_deleted}")
        else:
            print("No booking ids found to delete.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
