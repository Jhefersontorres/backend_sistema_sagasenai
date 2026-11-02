from contextlib import contextmanager


DISCLOSURE_LOCK_NAME = "sistema_gp:disclosure"
POSTGRES_DISCLOSURE_LOCK_ID = 7_302_026_093_000_001


@contextmanager
def disclosure_lock(connection):
    cursor = connection.cursor()
    acquired = False
    try:
        if getattr(connection, "dialect", None) == "sqlite":
            cursor.execute("BEGIN IMMEDIATE")
            yield
            return

        if getattr(connection, "dialect", None) == "postgresql":
            cursor.execute(
                "SELECT pg_advisory_xact_lock(%s)",
                (POSTGRES_DISCLOSURE_LOCK_ID,),
            )
            yield
            return

        cursor.execute("SELECT GET_LOCK(%s, %s)", (DISCLOSURE_LOCK_NAME, 10))
        row = cursor.fetchone()
        if not row or row[0] != 1:
            raise RuntimeError("Could not acquire the disclosure database lock.")
        acquired = True
        yield
    finally:
        try:
            if acquired:
                cursor.execute(
                    "SELECT RELEASE_LOCK(%s)",
                    (DISCLOSURE_LOCK_NAME,),
                )
                row = cursor.fetchone()
                if not row or row[0] != 1:
                    raise RuntimeError("Could not release the disclosure database lock.")
        finally:
            cursor.close()
