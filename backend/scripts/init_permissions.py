#!/usr/bin/env python3
"""
Seed the permission catalog and optionally assign all permissions to a user.

Usage:
  # Seed catalog only (idempotent):
  docker compose exec backend python scripts/init_permissions.py

  # Seed + assign all permissions to a user by username:
  docker compose exec backend python scripts/init_permissions.py --assign-username german
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.permission_service import (
    seed_permissions,
    assign_all_permissions_to_user,
    backfill_permissions,
)
from app.models.sql.user import User
from app.core.database import SessionLocal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed permissions catalog")
    parser.add_argument(
        "--assign-username",
        help="Assign all permissions to the given user after seeding",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Assign all permissions to every user with zero permissions",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        perms = seed_permissions(db)
        print(f"Permission catalog ready: {len(perms)} permissions")

        if args.backfill:
            results = backfill_permissions(db)
            if results:
                for username, count in results.items():
                    print(f"  Assigned {count} perms to user '{username}'")
            else:
                print("  All users already have permissions")

        if args.assign_username:
            user = db.query(User).filter(User.username == args.assign_username).first()
            if not user:
                print(f"ERROR: user '{args.assign_username}' not found")
                sys.exit(1)
            n = assign_all_permissions_to_user(db, user)
            print(f"  Assigned {n} new permissions to '{user.username}' ({len(user.permissions)} total)")
    finally:
        db.close()
