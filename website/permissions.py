from flask import Blueprint, render_template, redirect, request, url_for, current_app ,jsonify as flask_jsonify
from flask_login import login_user, login_required, logout_user, current_user, login_manager
import psycopg2
from .models import connection, User
from werkzeug.utils import secure_filename
import os

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

    return render_template("admin.html")


@permissions.route('/find-barbershop', methods=['POST'])
@login_required
def find_barbershop():
    if request.method == 'POST':
        barbershop_name = request.form.get('barbershop-name')
        with connection.cursor() as cur:
            cur.execute("SELECT barbershop_id, barbershop_name, address FROM barbershops WHERE barbershop_name ILIKE %s", ('%' + barbershop_name + '%',))
            search_results = cur.fetchall()
            print(f"results: {search_results}")
        results_html = ''
        if search_results:
            for result in search_results:
                results_html += f'<div class="search-result-item" data-id="{result[0]}">{result[1]}, Location: {result[2]}</div>'
        else:
            results_html = '<div class="search-result-item">No barbershops found</div>'
        return flask_jsonify({'results_html': results_html})
    return render_template("admin.html")



@permissions.route('/edit-barbershop', methods=['GET', 'POST'])
@login_required
def edit_barbershop():
    if request.method == 'POST':
        barbershop_name = request.form.get('barbershop-name')
        print(barbershop_name)
    return render_template("admin.html")











