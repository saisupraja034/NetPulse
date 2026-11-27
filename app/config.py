from os import getenv

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()

DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = int(getenv("DB_PORT", "3306"))
DB_NAME = getenv("DB_NAME", "netpulse")
DB_USER = getenv("DB_USER", "netpulse")
DB_PASSWORD = getenv("DB_PASSWORD", "")

DATABASE_URL = getenv("DATABASE_URL") or URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
).render_as_string(hide_password=False)