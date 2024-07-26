# views.py
from flask import Blueprint, Flask, request, render_template, redirect, url_for, session, current_app, flash, send_file
import io
from flask import jsonify as flask_jsonify
from .data import target_cuts, barbers_list
from .models import User, connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
import os
from flask_login import current_user, login_required
import psycopg2

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
    return render_template("target-haircut.html", haircuts=target_cuts, barbershop=barbershop)


@views.route('/locations/target-haircut/barbers', methods=['GET', 'POST'])
def barbers():
    barbershop = session.get('global_barbershop')
    haircut = session.get('global_haircut')
    if request.method == 'POST':
        selected_barber = request.form.get('choose')
        session['global_barber'] = selected_barber
        return redirect(url_for("views.days"))
    return render_template("barbers.html", barbers=barbers_list)


@views.route('/locations/target-haircut/barbers/available-days/', methods=['GET', 'POST'])
def days():
    if request.method == 'POST':
        day = request.form.get('day')
        session['day'] = day
        if not day:
            raise ValueError
        else:
            return redirect(url_for("views.hours"))
    return render_template("available-days.html")


@views.route('/locations/target-haircut/barbers/available-days/available-hours', methods=['GET', 'POST'])
def hours():
    day = session.get('day')
    if request.method == 'POST':
        time = request.form.get('hour')
        session['time'] = time
        if not time:
            raise ValueError
        else:
            return redirect(url_for("views.final"))
    return render_template('available-hours.html')


@views.route('/locations/target-haircut/barbers/available-days/available-hours/final-draft')
def final():
    barbershop = session.get('global_barbershop')
    haircut = session.get('global_haircut')
    barber = session.get('global_barber')
    day = session.get('day')
    time = session.get('time')

    selected_barbershop = next((shop for shop in barbershops if shop['barbershop_name'] == barbershop), None)
    selected_haircut = next((cut for cut in target_cuts if cut['haircut'] == haircut), None)
    selected_barber = next((brb for brb in barbers_list if brb['name'] == barber), None)

    if selected_barbershop is None:
        selected_barbershop = {'barbershop_name': barbershop, 'location': 'N/A'}

    if selected_haircut is None:
        selected_haircut = {'name': haircut, 'price': 'N/A'}

    if selected_barber is None:
        selected_barber = {'name': barber, 'rating': 'N/A'}

    return render_template('final-draft.html', barbershop=selected_barbershop, barber=selected_barber,
                           haircut=selected_haircut, day=day, time=time)


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
