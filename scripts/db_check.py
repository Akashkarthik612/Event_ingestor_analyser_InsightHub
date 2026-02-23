from sqlalchemy import inspect
import sys

from app.core.config import DATABASE_URL
import app.db.session as session

engine = getattr(session, 'engine', None)
print("DATABASE_URL:", DATABASE_URL)
print("Engine:", engine)

if engine is None:
    print("No engine found in session module", file=sys.stderr)
    sys.exit(2)

try:
    insp = inspect(engine)
    tables = insp.get_table_names()
    print("Tables found:", tables)
except Exception as e:
    print("ERROR while inspecting DB:", e, file=sys.stderr)
    raise
