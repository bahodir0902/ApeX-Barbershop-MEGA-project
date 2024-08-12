import psycopg2
from flask_login import UserMixin

connection = psycopg2.connect(
    host="localhost",
    database="Apex Barbershop",
    user="postgres",
    password="Bahodir2005"
)

cur = connection.cursor()

cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'privacy') THEN
            CREATE TYPE privacy AS ENUM ('private', 'public');
        END IF;
    END $$;
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT UNIQUE,
        phone_number VARCHAR(30) UNIQUE,
        password TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        privacy privacy DEFAULT 'private',
        profile_picture BYTEA,
        is_owner BOOLEAN DEFAULT FALSE
    )
""")
cur.execute("""
    UPDATE users SET created_date = date_trunc('second', created_date)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS barbershops (
	barbershop_id SERIAL PRIMARY KEY,
	owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	barbershop_name VARCHAR(100) NOT NULL,
	address TEXT NOT NULL,
	barbershop_picture BYTEA,
	barbershop_phone_number VARCHAR(30),
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS barbers(
	barber_id SERIAL PRIMARY KEY,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	barber_first_name VARCHAR(100) NOT NULL,
	barber_last_name VARCHAR(100),
	barber_phone_number VARCHAR(30) UNIQUE,
	barber_rating VARCHAR(10) DEFAULT 'N/A',
	barber_picture BYTEA,
	barber_email TEXT UNIQUE,
	experienced_years INTEGER,
	working_start_time TIME,
	working_end_time TIME,
	break_start_time TIME,
	break_end_time TIME,
	working_days VARCHAR(100),
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS haircuts(
	haircut_id SERIAL PRIMARY KEY,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	haircut_name TEXT NOT NULL,
	description TEXT,
	price DECIMAL(10, 2) DEFAULT 0,
	haircut_picture BYTEA,
	haircut_duration INTERVAL,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS barber_haircuts(
	barber_haircut_id SERIAL PRIMARY KEY,
	barber_id INTEGER REFERENCES barbers(barber_id) ON DELETE CASCADE,
	haircut_id INTEGER REFERENCES haircuts(haircut_id) ON DELETE CASCADE,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS permissions(
	permission_id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	can_edit BOOLEAN DEFAULT FALSE,
	can_delete BOOLEAN DEFAULT FALSE,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
""")

cur.execute("""CREATE TABLE IF NOT EXISTS appointments(
	appointment_id SERIAL PRIMARY KEY,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	barber_id INTEGER REFERENCES barbers(barber_id) ON DELETE CASCADE,
	customer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	haircut_id INTEGER REFERENCES haircuts(haircut_id) ON DELETE CASCADE,
	appointment_date DATE NOT NULL,
	appointment_time TIME NOT NULL,
	duration_minutes INTEGER DEFAULT 45,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
""")
connection.commit()



class User(UserMixin):
    def __init__(self, id, first_name, last_name, email, phone_number, password, created_date, privacy, profile_picture, is_owner):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.created_date = created_date
        self.profile_picture = profile_picture
        self.privacy = privacy
        self.is_owner = is_owner

    @staticmethod
    def get(user_id):
        # Implement a method to get a user by ID
        # e.g., SELECT * FROM users WHERE id = user_id
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                return User(*user_data)
            return None
