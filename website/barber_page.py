from flask import Flask, Blueprint, request, render_template, redirect, session, url_for, current_app, jsonify
import psycopg2
from .models import connection, User
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename


barber_page = Blueprint('barber_page', __name__)
cur = connection.cursor()


@barber_page.route('/get-haircuts', methods=['GET'])
@login_required
def get_haircuts():
    barber_id = current_user.barber_id
    print(f"barber id: {barber_id}")
    with connection.cursor() as cur:
        cur.execute("""SELECT h.haircut_id, h.haircut_name, h.description, h.price 
                       FROM haircuts h 
                       JOIN barber_haircuts bh ON bh.haircut_id = h.haircut_id 
                       WHERE bh.barber_id = %s""", (barber_id,))
        haircuts = cur.fetchall()
        cur.execute("""SELECT a.appointment_id,  a.appointment_time, a.appointment_date,
            u.first_name, u.last_name, u.phone_number, u.email,
            h.haircut_name, h.price, a.duration_minutes, a.created_date
            FROM appointments a
            JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
            JOIN barbers b ON a.barber_id = b.barber_id
            JOIN haircuts h ON a.haircut_id = h.haircut_id
            JOIN users u ON u.id = a.customer_id
            WHERE a.barber_id = %s AND is_active = true AND is_finished = false
            ORDER BY a.appointment_date, a.appointment_time""", (barber_id,))
        appointments = cur.fetchall()

        cur.execute("""SELECT a.appointment_id,  a.appointment_time, a.appointment_date,
                    u.first_name, u.last_name, u.phone_number, u.email,
                    h.haircut_name, h.price, a.duration_minutes, a.created_date
                    FROM appointments a
                    JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
                    JOIN barbers b ON a.barber_id = b.barber_id
                    JOIN haircuts h ON a.haircut_id = h.haircut_id
                    JOIN users u ON u.id = a.customer_id
                    WHERE a.barber_id = %s AND is_active = true AND is_finished = true
                    ORDER BY a.appointment_date, a.appointment_time""", (barber_id,))
        finished_appointments = cur.fetchall()

        cur.execute("""SELECT a.appointment_id,  a.appointment_time, a.appointment_date,
                            u.first_name, u.last_name, u.phone_number, u.email,
                            h.haircut_name, h.price, a.duration_minutes, a.created_date
                            FROM appointments a
                            JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
                            JOIN barbers b ON a.barber_id = b.barber_id
                            JOIN haircuts h ON a.haircut_id = h.haircut_id
                            JOIN users u ON u.id = a.customer_id
                            WHERE a.barber_id = %s AND is_active = false
                            ORDER BY a.appointment_date, a.appointment_time""", (barber_id,))
        canceled_appointments = cur.fetchall()
    print(f"appointments: {appointments}")
    return render_template("barber-page.html", haircuts=haircuts, appointments=appointments,
                           finished_appointments=finished_appointments, canceled_appointments=canceled_appointments)


@barber_page.route('/add-haircut', methods=['POST'])
@login_required
def add_haircut():
    if request.method == 'POST':
        haircut_name = request.form.get('haircut-name')
        haircut_price = request.form.get('haircut-price')
        haircut_description = request.form.get('haircut-description')
        picture = request.files.get('haircut-picture')
        barber_id = current_user.barber_id
        if picture:
            filename = secure_filename(picture.filename)
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
            picture_upload_folder = current_app.config['UPLOAD_FOLDER']
            picture_file_path = os.path.join(picture_upload_folder, filename)

            if not os.path.exists(picture_upload_folder):
                os.makedirs(picture_upload_folder)
            try:
                picture.save(picture_file_path)
                try:
                    with open(picture_file_path, 'rb') as f:
                        binary_data = f.read()
                        haircut_picture = psycopg2.Binary(binary_data)
                except Exception as e:
                    print(f"An error has occurred while saving a file")
            except Exception as e:
                print(f"An error has occurred while storing a file")

        print(f"barber id: {barber_id}")

        with connection.cursor() as cur:
            cur.execute("SELECT barbershop_id FROM barbers WHERE barber_id = %s", (barber_id,))
            barbershop_id = cur.fetchone()
            cur.execute("""INSERT INTO haircuts(barbershop_id, haircut_name, description, price, haircut_picture) VALUES (%s, %s, %s, %s, %s) 
            RETURNING haircut_id""", (barbershop_id, haircut_name, haircut_description, haircut_price, haircut_picture))
            haircut_id = cur.fetchone()
            cur.execute("""INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(%s, %s)""", (barber_id, haircut_id))
            connection.commit()

    barber_id = current_user.barber_id
    with connection.cursor() as cur:
        cur.execute("""SELECT h.haircut_id, h.haircut_name, h.description, h.price FROM haircuts h JOIN barber_haircuts bh 
                ON bh.haircut_id = h.haircut_id WHERE bh.barber_id = %s""", (barber_id,))
        haircuts = cur.fetchall()
    return redirect(url_for("views.barber_page_get", haircuts=haircuts))

@barber_page.route('/edit-haircuts', methods=['POST'])
@login_required
def edit_haircut():
    barber_id = current_user.barber_id
    with connection.cursor() as cur:
        cur.execute("""SELECT h.haircut_id, h.haircut_name, h.description, h.price FROM haircuts h JOIN barber_haircuts bh 
            ON bh.haircut_id = h.haircut_id WHERE bh.barber_id = %s""", (barber_id,))
        haircuts = cur.fetchall()
    if request.method == 'POST':
        selected_haircut = request.form.get('selected_haircut')
        haircut_name = request.form.get('haircut-name')
        haircut_price = request.form.get('haircut-price')
        haircut_description = request.form.get('haircut-description')
        picture = request.files.get('haircut-picture')
        fields_to_update = {}
        if picture:
            filename = secure_filename(picture.filename)
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
            picture_upload_folder = current_app.config['UPLOAD_FOLDER']
            picture_file_path = os.path.join(picture_upload_folder, filename)
            if not os.path.exists(picture_upload_folder):
                os.makedirs(picture_upload_folder)
            try:
                picture.save(picture_file_path)
                try:
                    with open(picture_file_path, 'rb') as f:
                        binary_data = f.read()
                        fields_to_update['haircut_picture'] = psycopg2.Binary(binary_data)
                except Exception as e:
                    print(f"An error has occurred while opening a file")
            except Exception as e:
                print(f"An error has occurred while storing a file")

        with connection.cursor() as cur:
            cur.execute("""SELECT * FROM haircuts WHERE haircut_id = %s""", (selected_haircut,))
            result = cur.fetchone()
            if haircut_name and haircut_name != result[2]:
                fields_to_update['haircut_name'] = haircut_name
            if haircut_price and haircut_price != result[4]:
                fields_to_update['price'] = haircut_price
            if haircut_description and haircut_description != result[3]:
                fields_to_update['description'] = haircut_description
            clause = ', '.join(f"{field} = %s" for field in fields_to_update)
            query = f"UPDATE haircuts SET {clause} WHERE haircut_id = %s"
            values = list(fields_to_update.values()) + [selected_haircut]
            cur.execute(query, values)
            connection.commit()

    return redirect(url_for("views.barber_page_get", haircuts=haircuts))


@barber_page.route('delete-haircut', methods=['POST'])
@login_required
def delete_haircut():
    barber_id = current_user.barber_id
    with connection.cursor() as cur:
        cur.execute("""SELECT h.haircut_id, h.haircut_name, h.description, h.price FROM haircuts h JOIN barber_haircuts bh 
                ON bh.haircut_id = h.haircut_id WHERE bh.barber_id = %s""", (barber_id,))
        haircuts = cur.fetchall()
    if request.method == 'POST':
        with connection.cursor() as cur:
            haircut_id = request.form.get('selected_haircut')
            print(f"Haircut id: {haircut_id}")
            cur.execute("DELETE FROM haircuts WHERE haircut_id = %s", (haircut_id,))
            cur.execute("DELETE FROM barber_haircuts WHERE haircut_id = %s", (haircut_id,))
            connection.commit()

    return redirect(url_for("views.barber_page_get", haircuts=haircuts))


@barber_page.route('/finish-appointment', methods=['POST'])
@login_required
def finish_appointment():
    appointment_id = request.form.get('appointment_id')
    with connection.cursor() as cur:
        cur.execute("UPDATE appointments SET is_finished = true WHERE appointment_id = %s", (appointment_id,))
        connection.commit()
    return redirect(url_for("views.barber_page_get"))


@barber_page.route('/cancel-appointment', methods=['POST'])
@login_required
def cancel_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        with connection.cursor() as cur:
            print(f"appointment_id: {appointment_id}")
            cur.execute("UPDATE appointments SET is_active = false WHERE appointment_id = %s", (appointment_id,))
            connection.commit()
            return redirect(url_for('views.barber_page_get'))
