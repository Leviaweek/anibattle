from psycopg_pool import ConnectionPool


def add_character(pool: ConnectionPool):
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("")