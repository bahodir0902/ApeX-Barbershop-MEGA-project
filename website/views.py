# views.py
from flask import Blueprint, Flask, request, render_template, redirect, url_for, session, current_app, flash, send_file, Response
import io
from flask import jsonify as flask_jsonify
from .models import User, connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
import os
from flask_login import current_user, login_required
import psycopg2
from datetime import timedelta, datetime

views = Blueprint("views", __name__)
cur = connection.cursor()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@views.route('/')
def home():
    return render_template("home.html", user=current_user)


@views.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        selected_barbershop = request.form.get('choose')
        session['global_barbershop'] = selected_barbershop
        return redirect(url_for("views.target_haircut"))
    cur.execute("""SELECT * FROM barbershops""")
    barbershops = cur.fetchall()

    return render_template("locations.html", barbershops=barbershops)


@views.route('/locations/target-haircut', methods=['POST', 'GET'])
def target_haircut():
    barbershop = session.get('global_barbershop')
    if request.method == 'POST':
        selected_haircut = request.form.get('choose')
        session['global_haircut'] = selected_haircut
        return redirect(url_for('views.barbers'))
    cur.execute("""SELECT DISTINCT * FROM haircuts WHERE barbershop_id = %s""", (barbershop,))
    haircuts = cur.fetchall()
    return render_template("target-haircut.html", haircuts=haircuts, barbershop=barbershop)


@views.route('/locations/target-haircut/barbers', methods=['GET', 'POST'])
def barbers():
    barbershop = session.get('global_barbershop')
    haircut = session.get('global_haircut')
    if request.method == 'POST':
        selected_barber = request.form.get('choose')
        session['global_barber'] = selected_barber
        return redirect(url_for("views.days"))
    cur.execute(f"SELECT DISTINCT b.barber_id, b.barber_first_name, b.barber_last_name,  b.barber_rating, b.barber_picture FROM barbers b JOIN  barber_haircuts bh ON b.barber_id = bh.barber_id JOIN  haircuts h ON bh.haircut_id = h.haircut_id WHERE h.haircut_name = %s; ", (haircut,))
    barbers_list = cur.fetchall()

    return render_template("barbers.html", barbers=barbers_list)


@views.route('/locations/target-haircut/barbers/available-days/', methods=['GET', 'POST'])
def days():
    if request.method == 'POST':
        day = request.form.get('day')
        session['day'] = datetime.strptime(day, '%d-%m-%Y').strftime('%Y-%m-%d')
        if not day:
            raise ValueError
        else:
            return redirect(url_for("views.hours"))
    barber_id = session.get('global_barber')
    cur.execute("SELECT working_days FROM barbers WHERE barber_id = %s", (barber_id,))
    result = cur.fetchone()
    working_days = result[0].split(', ')

    today = datetime.today()
    next_month = today + timedelta(days=30)
    available_dates = []

    current_date = today
    while current_date <= next_month:
        if current_date.strftime('%A') in working_days:
            available_dates.append(current_date.strftime('%d-%m-%Y'))
        current_date += timedelta(days=1)

    return render_template("available-days.html", available_days=available_dates)


@views.route('/locations/target-haircut/barbers/available-days/available-hours', methods=['GET', 'POST'])
def hours():
    day = session.get('day')
    barber_id = session.get('global_barber')
    if request.method == 'POST':
        time = request.form.get('hour')
        session['time'] = time
        if not time:
            raise ValueError
        else:
            return redirect(url_for("views.final"))

    cur.execute("SELECT working_start_time, working_end_time, break_start_time, break_end_time FROM barbers WHERE barber_id = %s", (barber_id,))
    result = cur.fetchone()
    working_start_time = result[0]
    working_end_time = result[1]
    break_start_time = result[2]
    break_end_time = result[3]
    cur.execute("SELECT appointment_time FROM appointments WHERE barber_id = %s AND appointment_date = %s", (barber_id, day))
    booked_slots = [row[0] for row in cur.fetchall()]


    available_hours = []
    current_time = working_start_time

    while current_time < working_end_time:
        if not (break_start_time < current_time < break_end_time) and current_time not in booked_slots:
            available_hours.append(current_time.strftime('%H:%M'))
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=45)).time()

    return render_template('available-hours.html', available_hours=available_hours)


@views.route('/locations/target-haircut/barbers/available-days/available-hours/final-draft')
def final():
    barbershop = session.get('global_barbershop')
    haircut = session.get('global_haircut')
    barber = session.get('global_barber')
    day = session.get('day')
    time = session.get('time')

    cur.execute("SELECT * FROM barbershops WHERE barbershop_id = %s", (barbershop,))
    barbershops = cur.fetchone()
    cur.execute("SELECT * FROM haircuts WHERE haircut_name = %s", (haircut,))
    target_cuts = cur.fetchone()
    cur.execute("SELECT * FROM barbers WHERE barber_id = %s", (barber,))
    barbers_list = cur.fetchone()

    """selected_barbershop = next((shop for shop in barbershops if shop['barbershop_id'] == barbershop), None)
    selected_haircut = next((cut for cut in target_cuts if cut['haircut_name'] == haircut), None)
    selected_barber = next((brb for brb in barbers_list if brb['barber_id'] == barber), None)"""

    """if selected_barbershop is None:
           selected_barbershop = {'barbershop_name': barbershop, 'location': 'N/A'}

       if selected_haircut is None:
           selected_haircut = {'name': haircut, 'price': 'N/A'}

       if selected_barber is None:
           selected_barber = {'name': barber, 'rating': 'N/A'}"""

    selected_barbershop = [barbershops[0], barbershops[2], barbershops[3]]
    selected_haircut = [target_cuts[0], target_cuts[2], target_cuts[4]]
    selected_barber = [barbers_list[0], barbers_list[2], barbers_list[6]]
    session['selected_barbershop'] = selected_barbershop
    session['selected_haircut'] = selected_haircut
    session['selected_barber'] = selected_barber

    return render_template('final-draft.html', barbershop=selected_barbershop, barber=selected_barber,
                           haircut=selected_haircut, day=day, time=time)

@views.route('/locations/target-haircut/barbers/available-days/available-hours/final-draft/book-now', methods = ['POST'])
@login_required
def book_now():
    user_id = request.form.get('user_id')
    if user_id != current_user.id:
        selected_barbershop = session.get('selected_barbershop')
        selected_haircut = session.get('selected_haircut')
        selected_barber = session.get('selected_barber')
        day = session.get('day')
        time = session.get('time')
        duration = 45
        print(f"barbershop: {selected_barbershop[0]}, barber: {selected_barber[0]}, haircut: {selected_haircut[0]}, day: {day}, time: {time}")
        cur.execute("SELECT COUNT(*) FROM appointments WHERE customer_id = %s AND appointment_date = %s AND appointment_time = %s", (current_user.id, day, time))
        result = cur.fetchone()[0]
        if result == 0:
            cur.execute("INSERT INTO appointments(barbershop_id, barber_id, customer_id, haircut_id, appointment_date, appointment_time, duration_minutes) VALUES(%s, %s, %s, %s, %s, %s ,%s)", (selected_barbershop[0], selected_barber[0], current_user.id, selected_haircut[0], day, time, duration))
            connection.commit()
        else:
            return 'You already have booked this order', 403
        return redirect(url_for('views.home'))
    else:
        return 'Unauthorized', 403


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        print('profile')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        privacy = request.form.get('privacy')

        current_password = session.get('current_password')
        print(current_password)
        new_password = session.get('new_password')
        print(new_password)


        # Save other form data to the database
        fields_to_update = {}
        if first_name != current_user.first_name:
            fields_to_update['first_name'] = first_name
        if last_name != current_user.last_name:
            fields_to_update['last_name'] = last_name
        if email != current_user.email:
            fields_to_update['email'] = email
        if phone_number != current_user.phone_number:
            fields_to_update['phone_number'] = phone_number
        if privacy != current_user.privacy:
            fields_to_update['privacy'] = privacy
        if new_password:
            fields_to_update['password'] = generate_password_hash(new_password, method='pbkdf2:sha256')
            print('success')
        else:
            return flask_jsonify(success=False, errors=["Error while changing the password."])
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
                upload_folder = current_app.config['UPLOAD_FOLDER']
                file_path = os.path.join(upload_folder, filename)

                # Ensure the upload directory exists
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    print(f"Created upload directory: {upload_folder}")

                try:
                    file.save(file_path)
                    print(f"File saved to: {file_path}")

                    try:
                        with open(file_path, 'rb') as f:
                            binary_data = f.read()
                        print(f"Binary data size: {len(binary_data)} bytes")
                        fields_to_update['profile_picture'] = psycopg2.Binary(binary_data)
                    except Exception as e:
                        print(f"Error reading file: {e}")

                except Exception as e:
                    print(f"File saving or reading error: {e}")
                    return flask_jsonify(success=False, errors=["Error saving or reading the file."])
        print(fields_to_update)
        if fields_to_update:
            try:
                with connection.cursor() as cur:
                    set_clause = ', '.join(f"{field} = %s " for field in fields_to_update)
                    query = f'UPDATE users SET {set_clause} WHERE id = %s'
                    values = list(fields_to_update.values()) + [current_user.id]
                    cur.execute(query, values)
                    connection.commit()

                # Return a JSON response indicating success
                return flask_jsonify(success=True, message="Profile updated successfully.")
            except Exception as e:
                print(f"An error has occurred: {e}")
                return flask_jsonify(success=False, errors=["An error occurred while updating the profile."])

        return flask_jsonify(success=True, message="No changes were made.")

    return render_template('profile.html', user=current_user)


@views.route('/profile_picture/<int:user_id>')
@login_required
def profile_picture(user_id):
    if user_id != current_user.id:
        return 'Unauthorized', 403
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT profile_picture FROM users WHERE id = %s", (user_id,))
            result = cur.fetchone()
            if result:
                binary_data = result[0]
                if binary_data:
                    # Serve the image
                    return send_file(
                        io.BytesIO(binary_data),
                        mimetype='image/jpeg',  # Adjust MIME type as needed
                        as_attachment=False,
                        download_name='profile_picture.jpg'  # Adjust filename as needed
                    )
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error retrieving image", 500

    return "Image not found", 404


@views.route('/get_picture/<string:category>/<int:item_id>')
def get_picture(category, item_id):
    global query_picture, query_id
    if category == 'barbershops':
        query_picture = 'barbershop_picture'
        query_id = 'barbershop_id'
    elif category == 'barbers':
        query_picture = 'barber_picture'
        query_id = 'barber_id'
    elif category == 'haircuts':
        query_picture = 'haircut_picture'
        query_id = 'haircut_id'

    with connection.cursor() as cur:
        query = f"SELECT {query_picture} FROM {category} WHERE {query_id} = %s"
        cur.execute(query, (item_id,))
        picture_data = cur.fetchone()
        # if picture_data is None or picture_data[0] is None:
        #     return "Image not found", 404
    return send_file(
                        io.BytesIO(picture_data[0]),
                        mimetype='image/jpeg',  # Adjust MIME type as needed
                        as_attachment=False,
                        download_name='picture.jpg'  # Adjust filename as needed
                    )
    #return Response(picture_data[0], mimetype='image/jpg') # this code IS MUCH MUCH MUCH slower!


@views.route('/settings')
def settings():
    return render_template("settings.html", user=current_user)


@views.route('/change_password', methods=['POST'])
@login_required
def change_password():
    print('Hello World')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    print("Current Password:", current_password)
    print("New Password:", new_password)
    print("Confirm New Password:", confirm_new_password)

    errors = []

    # Verify the current password
    if not check_password_hash(current_user.password, current_password):
        errors.append('Current password is incorrect.')
        print("Current password is incorrect.")
    elif new_password != confirm_new_password:
        errors.append('New passwords do not match.')
        print("New passwords do not match.")
    else:
        session['current_password'] = current_password
        session['new_password'] = new_password

        # Update the password in the database
        """new_password_hash = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password_hash, current_user.id))
        connection.commit()"""

        return flask_jsonify(success=True, message='Password updated successfully.')

    return flask_jsonify(success=False, errors=errors)


@views.route('/my-orders')
@login_required
def my_orders():
    cur.execute("""SELECT bs.barbershop_name, b.barber_first_name, b.barber_last_name,
        h.haircut_name, a.appointment_date, 
        a.appointment_time, a.duration_minutes
        FROM appointments a
        JOIN barbershops bs ON a.barbershop_id = bs.barbershop_id
        JOIN barbers b ON a.barber_id = b.barber_id
        JOIN haircuts h ON a.haircut_id = h.haircut_id
        WHERE customer_id = %s
        ORDER BY a.appointment_date, a.appointment_time
        """, (current_user.id,))

    appointments = cur.fetchall()
    print(f"appointments: {appointments}")
    return render_template("my-orders.html", appointments=appointments)


@views.route('/administration')
@login_required
def admin():
    return render_template("admin.html")