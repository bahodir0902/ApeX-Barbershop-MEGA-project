from flask import Flask, Blueprint, request, render_template, redirect, session, url_for, current_app, jsonify
import psycopg2
from .models import connection, User
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime

barber_page = Blueprint('barber_page', __name__)
cur = connection.cursor()


@barber_page.route('/get-haircuts', methods=['GET'])
@login_required
def get_haircuts():
    with connection.cursor() as cur:
        cur.execute("""SELECT is_barber FROM users WHERE id = %s""", (current_user.id,))
        result = cur.fetchone()
    if not result[0]:
        return redirect(url_for('views.home'))
    else:
        barber_id = current_user.barber_id
        print(f"barber id: {barber_id}")
        with connection.cursor() as cur:
            cur.execute("""SELECT DISTINCT h.haircut_id, h.haircut_name, h.description, h.price 
                           FROM haircuts h 
                           JOIN barber_haircuts bh ON bh.haircut_id = h.haircut_id 
                           WHERE bh.barber_id = %s AND TRIM(h.haircut_name) <> ''""", (barber_id,))
            haircuts = cur.fetchall()
            cur.execute("""SELECT a.appointment_id, a.appointment_time, a.appointment_date,
                u.first_name, u.last_name, u.phone_number, u.email,
                h.haircut_name, h.price, a.duration_minutes, a.created_date, a.user_comment
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

            cur.execute("""SELECT working_start_time, working_end_time,
                break_start_time, break_end_time, working_days
                FROM barbers WHERE barber_id = %s""", (barber_id,))
            schedules = cur.fetchall()

            cur.execute("""SELECT 
                SUM(CASE WHEN a.appointment_date = CURRENT_DATE THEN h.price ELSE 0 END) AS daily_total,
                SUM(CASE WHEN date_trunc('week', a.appointment_date) = date_trunc('week', CURRENT_DATE) THEN h.price ELSE 0 END) AS weekly_total,
                SUM(CASE WHEN date_trunc('month', a.appointment_date) = date_trunc('month', CURRENT_DATE) THEN h.price ELSE 0 END) AS monthly_total,
                SUM(h.price) AS absolute_total
                FROM haircuts h 
                JOIN barber_haircuts bh ON bh.haircut_id = h.haircut_id 
                JOIN appointments a ON a.barber_id = bh.barber_id
                WHERE bh.barber_id = %s AND a.is_finished = TRUE;
            """, (barber_id,))
            revenues = cur.fetchone()
            print(f"revenue: {revenues}")
            cur.execute("""SELECT 
                COUNT(CASE WHEN appointment_date = CURRENT_DATE THEN 1 END) AS daily_count,
                COUNT(CASE WHEN date_trunc('week', appointment_date) = date_trunc('week', CURRENT_DATE) THEN 1 END) AS weekly_count,
                COUNT(CASE WHEN date_trunc('month', appointment_date) = date_trunc('month', CURRENT_DATE) THEN 1 END) AS monthly_count,
                COUNT(appointment_id) AS total_count
                FROM appointments 
                WHERE barber_id = %s AND is_finished = TRUE;
            """, (barber_id,))
            total_appointments = cur.fetchone()
            cur.execute("""SELECT 
                COUNT(CASE WHEN is_active = FALSE AND is_finished = FALSE THEN 1 END) AS total_canceled_count
                FROM appointments 
                WHERE barber_id = %s""", (barber_id,))
            total_canceled_appointments = cur.fetchone()
            cur.execute("""SELECT AVG(feedback_star) 
                FROM feedbacks
                WHERE barber_id = %s
            """, (barber_id,))
            average_rating = cur.fetchone()[0]
            if average_rating:
                average_rating = round(average_rating, 1)
            else:
                average_rating = 'N/A'

            cur.execute("SELECT feedback_comment FROM feedbacks WHERE barber_id = %s", (barber_id,))
            feedback_comments_raw = cur.fetchall()
            feedback_comments = [comment[0] for comment in feedback_comments_raw]

            print(f'feedback comments: {feedback_comments}')
        return render_template("barber-page.html", haircuts=haircuts, appointments=appointments,
            finished_appointments=finished_appointments, canceled_appointments=canceled_appointments, schedules=schedules,
            revenues=revenues, total_appointments=total_appointments, total_canceled_appointments=total_canceled_appointments,
            average_rating=average_rating, feedback_comments=feedback_comments)


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


@barber_page.route('/update-schedule', methods=['POST'])
@login_required
def update_schedule():
    barber_id = current_user.barber_id
    working_start_time = request.form.get('working-start-time')
    working_end_time = request.form.get('working-end-time')
    break_start_time = request.form.get('break-start-time')
    break_end_time = request.form.get('break-end-time')
    working_days = request.form.getlist('working-days')

    fields_to_update = {}

    with connection.cursor() as cur:
        # Fetch the current schedule from the database
        cur.execute("""
            SELECT working_start_time, working_end_time,
                   break_start_time, break_end_time, working_days
            FROM barbers 
            WHERE barber_id = %s
        """, (barber_id,))
        result = cur.fetchone()  # fetchone is better if you expect a single result

        # Compare and update fields only if they differ
        if working_start_time and working_start_time != result[0].strftime('%H:%M:%S'):
            fields_to_update['working_start_time'] = working_start_time
        if working_end_time and working_end_time != result[1].strftime('%H:%M:%S'):
            fields_to_update['working_end_time'] = working_end_time
        if break_start_time and break_start_time != result[2].strftime('%H:%M:%S'):
            fields_to_update['break_start_time'] = break_start_time
        if break_end_time and break_end_time != result[3].strftime('%H:%M:%S'):
            fields_to_update['break_end_time'] = break_end_time
        if working_days:
            formatted_working_days = ', '.join(working_days)
            if formatted_working_days != result[4]:
                fields_to_update['working_days'] = formatted_working_days

        # Construct the update query only if there are changes
        if fields_to_update:
            clause = ', '.join(f"{field} = %s" for field in fields_to_update)
            query = f"UPDATE barbers SET {clause} WHERE barber_id = %s"
            values = list(fields_to_update.values()) + [barber_id]
            cur.execute(query, values)
            connection.commit()

    return redirect(url_for('views.barber_page_get'))
