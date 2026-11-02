from contextlib import contextmanager


@contextmanager
def managed_connection(get_connection):
    connection = get_connection()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@contextmanager
def managed_cursor(connection, *, dictionary=False):
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
    finally:
        cursor.close()
