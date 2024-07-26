# data.py

barbershops = [
    {'id': '1', 'barbershop_name': 'Barbershop №1', 'location': 'Muxtor Ashrafiy 21B', 'image_url': "/static/images/frame5.png"},
    {'id': '2', 'barbershop_name': 'Akmal Tamo', 'location': 'Yunusobod', 'image_url': "/static/images/frame6.png"},
    {'id': '3', 'barbershop_name': 'Sodir', 'location': 'Integro', 'image_url': "/static/images/frame7.png"},
    {'id': '4', 'barbershop_name': 'M19', 'location': 'Shota Rustavelli 21B', 'image_url': "/static/images/frame3.png"},
    {'id': '5', 'barbershop_name': 'Usta Husan', 'location': 'Risoviy Bozor', 'image_url': "/static/images/frame43.png"},
    {'id': '6', 'barbershop_name': 'Botir Barber', 'location': 'Ziyolilar 9', 'image_url': "/static/images/frame4.png"}
]

target_cuts = [
    {'id': '1', 'haircut': 'Crew Cut', 'price': '70 000', 'image_url': "/static/images/frame22.png"},
    {'id': '2', 'haircut': 'Buzz', 'price': '60 000', 'image_url': "/static/images/frame27.png"},
    {'id': '3', 'haircut': 'Beard Trim', 'price': '40 000', 'image_url': "/static/images/frame25.png"},
    {'id': '4', 'haircut': 'Shave', 'price': '50 000', 'image_url': "/static/images/frame23.png"},
    {'id': '5', 'haircut': 'Taper', 'price': '60 000', 'image_url': "/static/images/frame22.png"},
    {'id': '6', 'haircut': 'Undercut', 'price': '55 000', 'image_url': "/static/images/frame27.png"}
]

barbers_list = [
    {'id': '1', 'name': 'Akbar', 'rating': '5.0', 'image_url': '/static/images/frame60.png'},
    {'id': '2', 'name': 'Botir', 'rating': '5.0', 'image_url': '/static/images/frame61.png'},
    {'id': '3', 'name': 'Jasur', 'rating': '4.9', 'image_url': '/static/images/frame62.png'},
    {'id': '4', 'name': 'Avaz', 'rating': '4.8', 'image_url': '/static/images/frame63.png'},
    {'id': '5', 'name': 'Ahmad', 'rating': '4.6', 'image_url': '/static/images/frame64.png'},
    {'id': '6', 'name': "Ma'ruf", 'rating': '4.4', 'image_url': '/static/images/frame65.png'}
]







"""SELECT * FROM users;

CREATE TABLE IF NOT EXISTS barbershops (
	barbershop_id SERIAL PRIMARY KEY,
	owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	barbershop_name VARCHAR(100) NOT NULL,
	address TEXT NOT NULL,
	barbershop_picture BYTEA,
	barbershop_phone_number VARCHAR(30),
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS barbers(
	barber_id SERIAL PRIMARY KEY,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	barber_first_name VARCHAR(100) NOT NULL,
	barber_last_name VARCHAR(100),
	barber_phone_number VARCHAR(30) UNIQUE,
	barber_email TEXT UNIQUE,
	barber_rating VARCHAR(10) DEFAULT "N/A",
	experienced_yeards INTEGER,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS haircuts(
	haircut_id SERIAL PRIMARY KEY,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	haircut_name TEXT NOT NULL,
	description TEXT,
	price DECIMAL(10, 2) NOT NULL,
	haircut_picture BYTEA,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS barber_haircuts(
	barber_haircut_id SERIAL PRIMARY KEY,
	barber_id INTEGER REFERENCES barbers(barber_id) ON DELETE CASCADE,
	haircut_id INTEGER REFERENCES haircuts(haircut_id) ON DELETE CASCADE,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions(
	permission_id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
	barbershop_id INTEGER REFERENCES barbershops(barbershop_id) ON DELETE CASCADE,
	can_edit BOOLEAN DEFAULT FALSE,
	can_delete BOOLEAN DEFAULT FALSE,
	created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'Barbershop №1', 'Muxtor Ashrafiy 21B', '+9988984498445');
INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'Akmal Tamo', 'Yunusobod Dehqon bozor', '+9984654646464');
INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'Sodir', 'Integro', '+998595959999');
INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'M19', 'Shota Rustavelli 85C', '+9988181818117');
INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'Usta Husan', 'Risoviy Bozor', '+9984492397991');
INSERT INTO  barbershops(owner_id, barbershop_name, address, barbershop_phone_number) VALUES (1, 'Botir Barber', 'Ziyolilar 9', '+9987191981791');


INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Akbar', 'Aliev', '998265346133', 'akmal@mail.com', '2');
INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Botir', 'Sayfullayev', '998645634634', 'botir.apexbarbershop@mail.com', '1');
INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Jasur', 'Faybullayev', '998245345354', 'jasur.apexbarbershop@mail.com', '3');
INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Avaz', 'Oxun', '998534527675', 'avaz.apexbarbershop@mail.com', '4');
INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Ahmad', 'Shamsiyev', '998856433434', 'ahmad.apexbarbershop@mail.com', '5');
INSERT INTO  barbers(barbershop_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_yeards) VALUES (13, 'Maruf', 'Botirov', '998645646453', 'maruf.apexbarbershop@mail.com', '1');

SELECT * FROM barbers;

INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Crew Cut', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '70000');
INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Buzz', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '60000');
INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Beard Trim', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '40000');
INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Shave', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '50000');
INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Taper', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '60000');
INSERT INTO haircuts(barbershop_id, haircut_name, description, price) VALUES(13, 'Undercut', 'IUIUg nuiiiu IJge injkgre INJK esnigw NJKnnwj', '55000');


INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(3,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(3,2);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(3,3);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(3,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(3,5);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,6);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,2);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,3);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(4,5);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(5,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(5,2);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(5,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(5,5);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(6,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(6,2);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(6,3);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(6,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(6,6);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,2);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,3);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,5);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(7,6);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(8,1);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(8,4);
INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(8,5);











"""









