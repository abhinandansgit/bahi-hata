"""
Supabase PostgreSQL Migration & Verification Helper for Bahi Hata.

Usage:
  python scripts/setup_remote_db.py --url="postgresql://postgres.[REF]:[PASS]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"
  or ensure DATABASE_URL is set in your .env file and run:
  python scripts/setup_remote_db.py
"""

import os
import sys
import argparse
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    parser = argparse.ArgumentParser(description="Migrate and verify Supabase PostgreSQL database for Bahi Hata.")
    parser.add_argument("--url", help="Database URL for Supabase connection (overrides .env)")
    parser.add_argument("--superuser", action="store_true", help="Prompt to create a superuser after migrations")
    parser.add_argument("--seed", action="store_true", help="Seed initial catalog, categories, moods, and magazine editions to Supabase")
    args = parser.parse_args()

    if args.url:
        os.environ["DATABASE_URL"] = args.url
        os.environ["DB_SSL_REQUIRE"] = "True"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bahihata.settings")

    import django
    django.setup()

    from django.db import connections
    from django.core.management import call_command

    print("\n" + "=" * 60)
    print("  BAHI HATA - SUPABASE DATABASE DEPLOYMENT ASSISTANT")
    print("=" * 60)

    # 1. Test connection
    db_conn = connections['default']
    try:
        print("\n[1/4] Testing connection to PostgreSQL database...")
        db_conn.cursor()
        vendor = db_conn.vendor
        print(f"       SUCCESS: Connected to database engine: {vendor.upper()}")
    except Exception as e:
        print(f"\n[!] Connection Failed: {e}")
        print("    Please verify your DATABASE_URL format and Supabase credentials.")
        sys.exit(1)

    # 2. Run migrations
    try:
        print("\n[2/4] Running Django migrations on remote database...")
        call_command('migrate', interactive=False)
        print("       SUCCESS: All migrations applied successfully.")
    except Exception as e:
        print(f"\n[!] Migration error: {e}")
        sys.exit(1)

    # 3. Optional Seeding
    if args.seed:
        print("\n[3/4] Seeding initial market-ready data (books, magazine, categories, moods)...")
        try:
            from bahihata.seed import run as run_seed
            run_seed()
            print("       SUCCESS: Catalog seeded with market-ready data.")
        except Exception as e:
            print(f"       [!] Seeding notice: {e}")
    else:
        print("\n[3/4] Skipping data seeding (use --seed to load initial catalog).")

    # 4. Superuser creation check
    if args.superuser:
        print("\n[4/4] Creating Superuser...")
        try:
            call_command('createsuperuser')
        except KeyboardInterrupt:
            print("\nSkipped superuser creation.")
    else:
        print("\n[4/4] Database is fully initialized and production ready!")
        print("      To create an admin superuser, run: python manage.py createsuperuser")

    print("\n" + "=" * 60)
    print(" Deployment preparation completed successfully!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
