from flask import Blueprint, render_template, redirect, request, url_for, current_app, jsonify as flask_jsonify, \
    session, flash
from flask_login import login_user, login_required, logout_user, current_user, login_manager
import psycopg2
from .models import connection, User
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

permissions = Blueprint("permissions", __name__)
cur = connection.cursor()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@permissions.route('/add-barbershop', methods=['GET', 'POST'])
@login_required
def add_barbershop():
    if request.method == 'POST':
        barbershop_name = request.form.get('barbershop-name')
        barbershop_location = request.form.get('barbershop-location')
        barbershop_phone_number = request.form.get('barbershop-phone-number')
        file = request.files['barbershop-picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                print(f"Upload folder created successfully")
            try:
                file.save(file_path)
                print(f"file saved to {file_path}")
                try:
                    with open(file_path, 'rb') as f:
                        binary_data = f.read()
                        barbershop_picture = psycopg2.Binary(binary_data)
                        cur.execute(
                            "INSERT INTO barbershops(barbershop_name, address, barbershop_phone_number, barbershop_picture) VALUES (%s, %s, %s, %s)",
                            (barbershop_name, barbershop_location, barbershop_phone_number, barbershop_picture))
                        connection.commit()
                        print(f"Barbershop {barbershop_name} successfully added to database")
                except Exception as e:
                    print(f"An error has occurred while opening a file {file_path}")
            except Exception as e:
                print("An error has occurred")
        else:
            print(f"An error has occurred while reading a file. File extension maybe insecure")

    return redirect(url_for('views.admin'))


@permissions.route('/find-barbershop', methods=['POST'])
@login_required
def find_barbershop():
    if request.method == 'POST':
        barbershop_name = request.form.get('barbershop-name')
        with connection.cursor() as cur:
            cur.execute(
                "SELECT barbershop_id, barbershop_name, address, barbershop_phone_number FROM barbershops WHERE barbershop_name ILIKE %s",
                ('%' + barbershop_name + '%',))
            search_results = cur.fetchall()
            results = [{"barbershop_id": row[0], "barbershop_name": row[1], "address": row[2],
                        "barbershop_phone_number": row[3]} for row in search_results]
            return flask_jsonify(results)
    return redirect(url_for('views.admin'))

@permissions.route('edit-barbershop', methods=['POST'])
@login_required
def edit_barbershop():
    with connection.cursor() as cur:
        barbershop_id = request.form.get('barbershop_id')
        barbershop_name = request.form.get('edit-barbershop-name')
        barbershop_location = request.form.get('edit-barbershop-location')
        barbershop_phone_number = request.form.get('edit-barbershop-phone-number')
        file = request.files['edit-barbershop-picture']
        cur.execute("SELECT * FROM barbershops WHERE barbershop_id = %s", (barbershop_id,))
        result = cur.fetchone()
        fields_to_update = {}
        if barbershop_name and barbershop_name != result[2]:
            fields_to_update['barbershop_name'] = barbershop_name
        if barbershop_location and barbershop_location != result[3]:
            fields_to_update['address'] = barbershop_location
        if barbershop_phone_number and barbershop_phone_number != result[5]:
            fields_to_update['barbershop_phone_number'] = barbershop_phone_number
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                print(f"Upload folder created successfully")
            try:
                file.save(file_path)
                print(f"file saved to {file_path}")
                try:
                    with open(file_path, 'rb') as f:
                        binary_data = f.read()
                        barbershop_picture = psycopg2.Binary(binary_data)
                        fields_to_update['barbershop_picture'] = barbershop_picture
                        print(f"{barbershop_name}'s picture successfully added to database")
                except Exception as e:
                    print(f"An error has occurred while opening a file {file_path}")
            except Exception as e:
                print("An error has occurred")
        else:
            print(f"No file uploaded")

        if fields_to_update:
            try:
                with connection.cursor() as cur:
                    clause = ', '.join(f"{field} = %s" for field in fields_to_update)
                    query = f"UPDATE barbershops SET {clause} WHERE barbershop_id = %s"
                    values = list(fields_to_update.values()) + [barbershop_id]
                    cur.execute(query, values)
                    connection.commit()
                    return redirect(url_for('views.admin'))
            except Exception as e:
                print(f'an error has occurred while updating barbershop information, {e}')
        else:
            print('no changes were made')
    return redirect(url_for('views.admin'))


@permissions.route('/get-barbers/<int:barbershop_id>', methods=['GET'])
@login_required
def get_barbers(barbershop_id):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT barber_id, barber_first_name, barber_last_name FROM barbers WHERE barbershop_id = %s
            ORDER BY barber_first_name, barber_last_name
        """, (barbershop_id,))
        barbers = cur.fetchall()

        # Construct a list of dictionaries excluding memoryview fields (e.g., barber_picture)
        barbers_list = [
            {
                'barber_id': barber[0],
                'barber_first_name': barber[1],
                'barber_last_name': barber[2],
            }
            for barber in barbers
        ]
    return flask_jsonify(barbers_list)


@permissions.route('/get-barber-details/<int:barbershop_id>/<int:barber_id>', methods=['GET'])
@login_required
def get_barber_details(barbershop_id, barber_id):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT barber_id, barber_first_name, barber_last_name, barber_phone_number, barber_email, experienced_years,
                   working_start_time, working_end_time, break_start_time, break_end_time, working_days 
            FROM barbers 
            WHERE barbershop_id = %s AND barber_id = %s
        """, (barbershop_id, barber_id))
        barber = cur.fetchone()

        if barber:
            barber_data = {
                'barber_id': barber[0],
                'barber_first_name': barber[1],
                'barber_last_name': barber[2],
                'barber_phone_number': barber[3],
                'barber_email': barber[4],
                'experienced_years': barber[5],
                'working_start_time': barber[6].strftime('%H:%M:%S') if barber[5] else None,
                'working_end_time': barber[7].strftime('%H:%M:%S') if barber[6] else None,
                'break_start_time': barber[8].strftime('%H:%M:%S') if barber[7] else None,
                'break_end_time': barber[9].strftime('%H:%M:%S') if barber[8] else None,
                'working_days': barber[10]  # Assuming this is a string like 'Monday, Tuesday, Friday'
            }
            return flask_jsonify(barber_data)
        else:
            return flask_jsonify({'error': 'Barber not found'}), 404


@permissions.route('/add-barber', methods=['POST'])
@login_required
def add_barber():
    with connection.cursor() as cur:
        barbershop_id = request.form.get('barbershop_id_hidden')
        settings_add_barber_first_name = request.form.get('add-barber-first-name')
        settings_add_barber_last_name = request.form.get('add-barber-last-name')
        settings_add_barber_phone_number = request.form.get('add-barber-phone-number')
        settings_add_barber_email = request.form.get('add-barber-email')
        settings_add_barber_experienced_years = request.form.get('add-barber-experienced-years')
        settings_add_barber_working_start_time = request.form.get('add-barber-working-start-time')
        settings_add_barber_working_end_time = request.form.get('add-barber-working-end-time')
        settings_add_barber_break_start_time = request.form.get('add-barber-break-start-time')
        settings_add_barber_break_end_time = request.form.get('add-barber-break-end-time')
        settings_add_barber_working_days = request.form.getlist('add-working-days')
        settings_add_barber_picture = request.files['add-barber-picture']
        if settings_add_barber_first_name or settings_add_barber_last_name or settings_add_barber_phone_number or settings_add_barber_email or settings_add_barber_experienced_years or settings_add_barber_working_start_time or settings_add_barber_working_end_time or settings_add_barber_break_start_time or settings_add_barber_break_end_time or settings_add_barber_working_days or settings_add_barber_picture:
            fields_to_add = {}
            if settings_add_barber_first_name:
                fields_to_add['barber_first_name'] = settings_add_barber_first_name
            if settings_add_barber_last_name:
                fields_to_add['barber_last_name'] = settings_add_barber_last_name
            if settings_add_barber_phone_number:
                fields_to_add['barber_phone_number'] = settings_add_barber_phone_number
            else:
                fields_to_add['barber_phone_number'] = ""
            if settings_add_barber_email:
                fields_to_add['barber_email'] = settings_add_barber_email
            else:
                fields_to_add['barber_phone_number'] = ""
            if settings_add_barber_experienced_years:
                fields_to_add['experienced_years'] = settings_add_barber_experienced_years
            if settings_add_barber_working_start_time:
                fields_to_add['working_start_time'] = settings_add_barber_working_start_time
            if settings_add_barber_working_end_time:
                fields_to_add['working_end_time'] = settings_add_barber_working_end_time
            if settings_add_barber_break_start_time:
                fields_to_add['break_start_time'] = settings_add_barber_break_start_time
            if settings_add_barber_break_end_time:
                fields_to_add['break_end_time'] = settings_add_barber_break_end_time
            if settings_add_barber_working_days:
                fields_to_add['working_days'] = ', '.join(settings_add_barber_working_days)
            if settings_add_barber_picture:
                filename = secure_filename(settings_add_barber_picture.filename)
                current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
                picture_upload_folder = current_app.config['UPLOAD_FOLDER']
                picture_file_path = os.path.join(picture_upload_folder, filename)

                if not os.path.exists(picture_upload_folder):
                    os.makedirs(picture_upload_folder)
                try:
                    settings_add_barber_picture.save(picture_file_path)
                    try:
                        with open(picture_file_path, 'rb') as f:
                            binary_data = f.read()
                            picture = psycopg2.Binary(binary_data)
                            fields_to_add['barber_picture'] = picture
                    except Exception as e:
                        print(f"An error has occurred while saving a file")
                except Exception as e:
                    print(f"An error has occurred while storing a file")

            password = generate_password_hash('1234', method='pbkdf2:sha256')
            column = ', '.join(fields_to_add.keys())
            placeholders = ', '.join(['%s'] * len(fields_to_add))
            add_query = f"INSERT INTO barbers ({column}, barbershop_id, password) VALUES ({placeholders}, %s, %s) RETURNING barber_id"
            add_values = list(fields_to_add.values())
            add_values.append(barbershop_id)
            add_values.append(password)
            cur.execute(add_query, add_values)
            barber_id = cur.fetchone()[0]
            cur.execute("""INSERT INTO users(first_name, last_name, email, phone_number, password, profile_picture, is_barber, barber_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (fields_to_add['barber_first_name'], fields_to_add['barber_last_name'],
                         fields_to_add['barber_email'], fields_to_add['barber_phone_number'], password,
                         fields_to_add['barber_picture'], 'true', barber_id
                         ))  # GO BACK HERE
            connection.commit()
    return redirect(url_for('views.admin'))

@permissions.route('edit-barber', methods=['POST'])
@login_required
def edit_barber():
    with connection.cursor() as cur:
        barbershop_id = request.form.get('barbershop_id_hidden')
        edit_barber_first_name = request.form.get('edit-barber-first-name')
        edit_barber_last_name = request.form.get('edit-barber-last-name')
        edit_barber_phone_number = request.form.get('edit-barber-phone-number')
        edit_barber_email = request.form.get('edit-barber-email')
        edit_barber_experienced_years = request.form.get('edit-barber-experienced-years')
        edit_barber_working_start_time = request.form.get('edit-barber-working-start-time')
        edit_barber_working_end_time = request.form.get('edit-barber-working-end-time')
        edit_barber_break_start_time = request.form.get('edit-barber-break-start-time')
        edit_barber_break_end_time = request.form.get('edit-barber-break-end-time')
        edit_barber_working_days = request.form.getlist('edit-working-days')
        edit_barber_picture = request.files.get('edit-barber-picture')
        if edit_barber_first_name or edit_barber_last_name or edit_barber_phone_number or edit_barber_email or edit_barber_experienced_years or edit_barber_working_start_time or edit_barber_working_end_time or edit_barber_break_start_time or edit_barber_break_end_time or edit_barber_working_days or edit_barber_picture:

            fields_to_edit = {}
            cur.execute("SELECT * FROM barbers WHERE barber_id = %s", (request.form.get('barber_id_hidden'),))
            result = cur.fetchone()
            if edit_barber_first_name and edit_barber_first_name != result[2]:
                fields_to_edit['barber_first_name'] = edit_barber_first_name
            if edit_barber_last_name and edit_barber_last_name != result[3]:
                fields_to_edit['barber_last_name'] = edit_barber_last_name
            if edit_barber_phone_number and edit_barber_phone_number != result[4]:
                fields_to_edit['barber_phone_number'] = edit_barber_phone_number
            if edit_barber_email and edit_barber_email != result[7]:
                fields_to_edit['barber_email'] = edit_barber_email
            if edit_barber_experienced_years and edit_barber_experienced_years != str(result[8]):
                fields_to_edit['experienced_years'] = edit_barber_experienced_years
            if edit_barber_working_start_time and edit_barber_working_start_time != result[9].strftime('%H:%M:%S'):
                fields_to_edit['working_start_time'] = edit_barber_working_start_time
            if edit_barber_working_end_time and edit_barber_working_end_time != result[10].strftime('%H:%M:%S'):
                fields_to_edit['working_end_time'] = edit_barber_working_end_time
            if edit_barber_break_start_time and edit_barber_break_start_time != result[11].strftime('%H:%M:%S'):
                fields_to_edit['break_start_time'] = edit_barber_break_start_time
            if edit_barber_break_end_time and edit_barber_break_end_time != result[12].strftime('%H:%M:%S'):
                fields_to_edit['break_end_time'] = edit_barber_break_end_time
            if edit_barber_working_days:
                fields_to_edit['working_days'] = ', '.join(edit_barber_working_days)

            if edit_barber_picture:
                filename = secure_filename(edit_barber_picture.filename)
                current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
                picture_upload_folder = current_app.config['UPLOAD_FOLDER']
                picture_file_path = os.path.join(picture_upload_folder, filename)

                if not os.path.exists(picture_upload_folder):
                    os.makedirs(picture_upload_folder)
                try:
                    edit_barber_picture.save(picture_file_path)
                    try:
                        with open(picture_file_path, 'rb') as f:
                            binary_data = f.read()
                            picture = psycopg2.Binary(binary_data)
                            fields_to_edit['barber_picture'] = picture
                    except Exception as e:
                        print(f"An error has occurred while saving a file")
                except Exception as e:
                    print(f"An error has occurred while storing a file")
            if fields_to_edit:
                try:
                    if fields_to_edit:
                        clause = ', '.join(f"{field} = %s" for field in fields_to_edit)
                        query = f"UPDATE barbers SET {clause} WHERE barbershop_id = %s AND barber_id = %s RETURNING barber_id"
                        values = list(fields_to_edit.values()) + [barbershop_id, request.form.get('barber_id_hidden')]
                        cur.execute(query, values)
                        connection.commit()

                except Exception as e:
                    print(f'An error occurred while updating barber information: {e}')
                    connection.rollback()
            else:
                print('No changes were made')

    return redirect(url_for('views.admin'))


@permissions.route('/delete-barbershops', methods=['POST'])
@login_required
def find_barbershop_to_delete():
    if request.method == 'POST':
        barbershop_name = request.form.get('delete-barbershop-name')
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM barbershops WHERE barbershop_name ILIKE  %s", ('%' + barbershop_name + '%',))
            search_result = cur.fetchall()
            result_html = ""
            for result in search_result:
                cur.execute("SELECT barber_first_name, barber_last_name FROM barbers WHERE barbershop_id = %s",
                            (result[0],))
                barbers = cur.fetchall()
                if barbers:
                    barbers_list = ''.join(f'<li>{barber[0]} {barber[1]}</li>' for barber in barbers)
                else:
                    barbers_list = ''.join(f'<li>No barbers.</li>')
                result_html += f'''
                <div class="delete-search-results" data-id="{result[0]}">
                    <div class="results-header" style="display: flex; justify-content: space-between;">
                        {result[2]}, Location: {result[3]}
                        <button class="btn btn-link p-0 toggle-delete-search-result-btn">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="delete-search-result-content" id="delete-search-result-content" style="display: none;">
                        <form id="delete-barbershop-form" method="POST" action="/delete_barbershop">
                            <div class="barbers-lists">
                                <h3 style="font-weight: 500; margin-top: 15px;">Barbers lists in '{result[2]}'</h3>
                                <ul class="ul-barbers" style="margin-top: 15px;">
                                    {barbers_list}
                                </ul> 
                            </div>
                            <div class="confirm-delete">
                                <input type="hidden" name="barbershop_id_to_delete" value={result[0]}>
                                <button type="submit">Delete barbershop <i class='bx bx-trash'></i></button>
                                <p style="margin: 15px;">Be advised that once this barbershop is deleted, the listed barbers will <b>remain in the system</b>, but their association with this barbershop will be removed.</p>
                            </div>
                        </form>
                    </div>
                </div>
                '''
            if not result_html:
                result_html = '<div class="delete-search-results">No barbershops found</div>'
        return flask_jsonify({'result_html': result_html})
    return render_template("admin.html")


@permissions.route('/delete-barber', methods=['POST'])
@login_required
def delete_barber():
    barber_id = request.form.get('barber_id_hidden')
    with connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE barber_id = %s", (barber_id,))
        cur.execute("DELETE FROM barbers WHERE barber_id = %s", (barber_id,))
        cur.execute("SELECT haircut_id FROM barber_haircuts WHERE barber_id = %s", (barber_id,))
        haircuts_id = cur.fetchall()
        cur.execute("DELETE FROM barber_haircuts WHERE barber_id = %s", (barber_id,))
        for haircut_id in haircuts_id:
            cur.execute("DELETE FROM haircuts WHERE haircut_id = %s", (haircut_id,))
        cur.execute("DELETE FROM appointments WHERE barber_id = %s", (barber_id,))
        connection.commit()
    return redirect(url_for('views.admin'))


@permissions.route('/delete_barbershop', methods=['POST'])
@login_required
def delete_barbershop():
    if request.method == 'POST':
        barbershop_id = request.form.get('barbershop_id_to_delete')
        with connection.cursor() as cur:
            cur.execute("DELETE FROM barbershops WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("UPDATE barbers SET barbershop_id = NULL WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("UPDATE haircuts SET barbershop_id = NULL WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("DELETE FROM appointments WHERE barbershop_id = %s", (barbershop_id,))
            connection.commit()
        return redirect(url_for('views.admin'))


@permissions.route('/add-appointment', methods=['POST'])
@login_required
def add_appointment():
    customer_first_name = request.form.get('customer-first-name')
    customer_last_name = request.form.get('customer-last-name')
    customer_phone_number = request.form.get('customer-phone-number')
    appointment_date = request.form.get('appointment-day')
    appointment_time = request.form.get('appointment_time')
    duration_minutes = request.form.get('duration_minutes')
    with connection.cursor() as cur:
        cur.execute("SELECT phone_number FROM users WHERE phone_number = %s", (customer_phone_number,))
        result = cur.fetchone()
        if not result:
            password = generate_password_hash('1234', method='pbkdf2:sha256')
            cur.execute(
                "INSERT INTO users(first_name, last_name, phone_number, password) VALUES(%s, %s, %s, %s) RETURNING id",
                (customer_first_name, customer_last_name, customer_phone_number, password))
            customer_id = cur.fetchone()
            connection.commit()
        else:
            cur.execute("SELECT id FROM users WHERE phone_number = %s", (customer_phone_number,))
            customer_id = cur.fetchone()
        barbershop_id = request.form.get('barbershop_id')
        barber_id = request.form.get('barber_id')
        haircut_id = request.form.get('haircut_id')[0]
        if not (barbershop_id and barber_id and haircut_id):
            flash("Invalid selection. Please select valid barbershop, barber, and haircut.")
            return redirect(url_for('views.admin'))
        cur.execute("""
            INSERT INTO appointments (barbershop_id, barber_id, customer_id, haircut_id, appointment_date, appointment_time, duration_minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (barbershop_id, barber_id, customer_id, haircut_id, appointment_date, appointment_time, duration_minutes))
        connection.commit()

    return redirect(url_for('views.admin'))


@permissions.route('/get_barber_id', methods=['POST'])
def get_barber_id():
    data = request.get_json()
    barber_id = data.get('barber_id')
    session['add-appointment-barber-id'] = barber_id
    return flask_jsonify({"status": "success", "received_barber_id": barber_id})


@permissions.route('/get-all-haircuts/<int:barber_id>', methods=['GET'])
def get_all_haircuts(barber_id):
    cur.execute("""
        SELECT DISTINCT h.haircut_id, h.haircut_name, h.price
        FROM haircuts h
        JOIN barber_haircuts bs ON h.haircut_id = bs.haircut_id
        WHERE bs.barber_id = %s AND TRIM(h.haircut_name) <> ''
    """, (barber_id,))
    results = cur.fetchall()
    return flask_jsonify([{"haircut_id": results[0],  "haircut_name": result[1], "price": result[2]} for result in results])


@permissions.route('/get-suggestions/<type>', methods=['GET'])
def get_suggestions(type):
    query = request.args.get('q', '')
    if type == 'barbershop':
        cur.execute("SELECT barbershop_name, barbershop_id FROM barbershops WHERE barbershop_name ILIKE %s",
                    (f'%{query}%',))
        results = cur.fetchall()
        return flask_jsonify([{"barbershop_name": result[0], "barbershop_id": result[1]} for result in results])

    elif type == 'barber':
        barbershop_id = request.args.get('barbershop_id')
        session['send_barbershop_id'] = barbershop_id
        if barbershop_id:
            cur.execute(
                "SELECT barber_first_name, barber_id FROM barbers WHERE barber_first_name ILIKE %s AND barbershop_id = %s",
                (f'%{query}%', barbershop_id))
            results = cur.fetchall()
            return flask_jsonify([{"barber_name": result[0], "barber_id": result[1]} for result in results])
        else:
            return flask_jsonify([])  # No barbershop ID provided


@permissions.route('/list-upcoming-appointments', methods=['GET'])
@login_required
def list_upcoming_appointments():
    with connection.cursor() as cur:
        cur.execute('''
        SELECT  a.appointment_id, a.customer_id, u.first_name, u.last_name, u.phone_number, 
            a.appointment_date, a.appointment_time, a.duration_minutes, 
            bs.barbershop_name, bs.address, b.barber_first_name, b.barber_last_name,
            h.haircut_name, h.price, a.created_date
            FROM appointments a 
            JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
            JOIN barbers b ON a.barber_id = b.barber_id
            JOIN haircuts h ON a.haircut_id = h.haircut_id
            JOIN users u ON a.customer_id = u.id
            WHERE a.is_finished = False AND a.is_active = True
            ORDER BY appointment_date, appointment_time
        ''')
        appointments = cur.fetchall()

    appointments_list = []
    for appointment in appointments:
        appointments_list.append({
            'appointment_id': appointment[0],
            'customer_id': appointment[1],
            'customer_first_name': appointment[2],
            'customer_last_name': appointment[3],
            'customer_phone_number': appointment[4],
            'appointment_date': appointment[5].strftime('%Y-%m-%d'),  # Convert date to string
            'appointment_time': appointment[6].strftime('%H:%M:%S'),  # Convert time to string
            'duration_minutes': appointment[7],
            'barbershop_name': appointment[8],
            'address': appointment[9],
            'barber_first_name': appointment[10],
            'barber_last_name': appointment[11],
            'haircut_name': appointment[12],
            'price': appointment[13],
            'created_date': appointment[14].strftime('%Y-%m-%d %H:%M:%S')  # Convert timestamp to string
        })

    return flask_jsonify({'appointments': appointments_list})


@permissions.route('/list-finished-appointments', methods=['GET'])
@login_required
def list_finished_appointments():
    with connection.cursor() as cur:
        cur.execute('''
        SELECT  a.appointment_id, a.customer_id, u.first_name, u.last_name, u.phone_number, 
            a.appointment_date, a.appointment_time, a.duration_minutes, 
            bs.barbershop_name, bs.address, b.barber_first_name, b.barber_last_name,
            h.haircut_name, h.price, a.created_date
            FROM appointments a 
            JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
            JOIN barbers b ON a.barber_id = b.barber_id
            JOIN haircuts h ON a.haircut_id = h.haircut_id
            JOIN users u ON a.customer_id = u.id
            WHERE a.is_finished = True AND a.is_active = True
            ORDER BY appointment_date, appointment_time
        ''')
        appointments = cur.fetchall()

    appointments_list = []
    for appointment in appointments:
        appointments_list.append({
            'appointment_id': appointment[0],
            'customer_id': appointment[1],
            'customer_first_name': appointment[2],
            'customer_last_name': appointment[3],
            'customer_phone_number': appointment[4],
            'appointment_date': appointment[5].strftime('%Y-%m-%d'),  # Convert date to string
            'appointment_time': appointment[6].strftime('%H:%M:%S'),  # Convert time to string
            'duration_minutes': appointment[7],
            'barbershop_name': appointment[8],
            'address': appointment[9],
            'barber_first_name': appointment[10],
            'barber_last_name': appointment[11],
            'haircut_name': appointment[12],
            'price': appointment[13],
            'created_date': appointment[14].strftime('%Y-%m-%d %H:%M:%S')  # Convert timestamp to string
        })

    return flask_jsonify({'appointments': appointments_list})


@permissions.route('/list-canceled-appointments', methods=['GET'])
@login_required
def list_canceled_appointments():
    with connection.cursor() as cur:
        cur.execute('''
        SELECT  a.appointment_id, a.customer_id, u.first_name, u.last_name, u.phone_number, 
            a.appointment_date, a.appointment_time, a.duration_minutes, 
            bs.barbershop_name, bs.address, b.barber_first_name, b.barber_last_name,
            h.haircut_name, h.price, a.created_date
            FROM appointments a 
            JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
            JOIN barbers b ON a.barber_id = b.barber_id
            JOIN haircuts h ON a.haircut_id = h.haircut_id
            JOIN users u ON a.customer_id = u.id
            WHERE a.is_finished = False AND a.is_active = False
            ORDER BY appointment_date, appointment_time
        ''')
        appointments = cur.fetchall()

    appointments_list = []
    for appointment in appointments:
        appointments_list.append({
            'appointment_id': appointment[0],
            'customer_id': appointment[1],
            'customer_first_name': appointment[2],
            'customer_last_name': appointment[3],
            'customer_phone_number': appointment[4],
            'appointment_date': appointment[5].strftime('%Y-%m-%d'),  # Convert date to string
            'appointment_time': appointment[6].strftime('%H:%M:%S'),  # Convert time to string
            'duration_minutes': appointment[7],
            'barbershop_name': appointment[8],
            'address': appointment[9],
            'barber_first_name': appointment[10],
            'barber_last_name': appointment[11],
            'haircut_name': appointment[12],
            'price': appointment[13],
            'created_date': appointment[14].strftime('%Y-%m-%d %H:%M:%S')  # Convert timestamp to string
        })

    return flask_jsonify({'appointments': appointments_list})


@permissions.route('/cancel-appointment', methods=['POST'])
@login_required
def cancel_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        with connection.cursor() as cur:
            cur.execute("UPDATE appointments SET is_active = false WHERE appointment_id = %s", (appointment_id,))
            connection.commit()
            return redirect(url_for('views.admin'))


@permissions.route('/delete-appointment', methods=['POST'])
@login_required
def delete_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        with connection.cursor() as cur:
            cur.execute("DELETE FROM appointments WHERE appointment_id = %s", (appointment_id,))
            connection.commit()
            return redirect(url_for('views.admin'))


@permissions.route('/get-available-dates', methods=['GET'])
def get_available_dates():
    barbershop_id = session.get('send_barbershop_id')
    barber_id = session.get('add-appointment-barber-id')
    available_dates = days(barber_id, barbershop_id)
    return flask_jsonify({'available_dates': available_dates})


@permissions.route('/get-available-times', methods=['GET'])
def get_available_times():
    barbershop_id = session.get('send_barbershop_id')
    barber_id = session.get('add-appointment-barber-id')
    day = request.args.get('day')
    available_times = hours(barber_id, barbershop_id, day)
    return flask_jsonify({'available_times': available_times})


def days(barber_id, barbershop_id):
    with connection.cursor() as cur:
        cur.execute("SELECT working_days FROM barbers WHERE barber_id = %s AND barbershop_id = %s",
                    (barber_id, barbershop_id))
        result = cur.fetchone()

        if not result:
            return ["In this day a barber will not work"]

        working_days = result[0].split(', ')
        today = datetime.today()
        next_month = today + timedelta(days=30)
        available_dates = []

        current_date = today
        while current_date <= next_month:
            current_day_name = current_date.strftime('%A')
            if current_day_name in working_days:
                available_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return available_dates


def hours(barber_id, barbershop_id, day):
    cur.execute(
        "SELECT working_days, working_start_time, working_end_time, break_start_time, break_end_time FROM barbers WHERE barber_id = %s AND barbershop_id = %s",
        (barber_id, barbershop_id))
    result = cur.fetchone()

    if not result:
        return ["In this day a barber will not work"]

    working_days = result[0].split(', ')
    working_start_time = result[1]
    working_end_time = result[2]
    break_start_time = result[3]
    break_end_time = result[4]

    # Convert the selected day to the day name
    selected_day_name = datetime.strptime(day, '%Y-%m-%d').strftime('%A')

    if selected_day_name not in working_days:
        return ["In this day a barber will not work"]

    cur.execute("""SELECT appointment_time FROM appointments WHERE barber_id = %s AND appointment_date = %s  
        AND is_finished = false AND is_active = true""", (barber_id, day))
    booked_slots = [row[0] for row in cur.fetchall()]

    available_hours = []
    current_time = working_start_time

    while current_time < working_end_time:
        if not (break_start_time <= current_time < break_end_time) and current_time not in booked_slots:
            available_hours.append(current_time.strftime('%H:%M'))
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=45)).time()

    if not available_hours:
        return ["NO AVAILABLE TIME FOR THIS DATE, PLEASE CHOOSE ANOTHER DAY"]

    return available_hours





