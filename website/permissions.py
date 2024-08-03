from flask import Blueprint, render_template, redirect, request, url_for, current_app, jsonify as flask_jsonify
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
            cur.execute(
                "SELECT barbershop_id, barbershop_name, address, barbershop_phone_number FROM barbershops WHERE barbershop_name ILIKE %s",
                ('%' + barbershop_name + '%',))
            search_results = cur.fetchall()
            print(f"results: {search_results}")
        results_html = ''
        if search_results:
            for result in search_results:
                # results_html += f'<div class="search-result-item" data-id="{result[0]}">{result[1]}, Location: {result[2]} <button class="btn btn-link p-0" id="toggle-search-results-btn1"><i class="fas fa-plus"></i></button></div>'
                results_html += f'''
        <div class="search-result-item" data-id="{result[0]}">
                    <div class="results-header d-flex justify-content-between align-items-center">
                        {result[1]}, Location: {result[2]}
                        <button class="btn btn-link p-0 toggle-search-result-btn">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="search-result-content" style="display: none;">
                        <form id="add-barbershop-form" enctype="multipart/form-data" method="POST"
                            action="/find_barbershop/edit-barbershop">
                                <div class="form-group">
                                    <label for="barbershop-name">Barbershop name</label>
                                    <input type="text" class="form-control" id="edit-barbershop-name" name="edit-barbershop-name" placeholder="{result[1]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-location">Barbershop location</label>
                                    <input type="text" class="form-control" id="edit-barbershop-location" name="edit-barbershop-location"
                                     placeholder="{result[2]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-phone-number">Barbershop owner's phone number</label>
                                     <input type="tel" class="form-control" id="edit-barbershop-phone-number" name="edit-barbershop-phone-number" placeholder="{result[3]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-picture">Barbershop picture</label>
                                    <input type="file" class="form-control" id="edit-barbershop-picture" name="edit-barbershop-picture">
                                </div>
                            <input type="hidden" name="barbershop_id" value="{result[0]}">
                            <button type="submit" class="btn btn-primary">Confirm Changes</button>
                        </form>
                    </div>
                </div>
        
'''
        else:
            results_html = '<div class="search-result-item">No barbershops found</div>'
        return flask_jsonify({'results_html': results_html})
    return render_template("admin.html")


@permissions.route('/find_barbershop/edit-barbershop', methods=['POST'])
@login_required
def edit_barbershop():
    if request.method == 'POST':
        with connection.cursor() as cur:
            barbershop_id = request.form.get('barbershop_id')
            barbershop_name = request.form.get('edit-barbershop-name')
            barbershop_location = request.form.get('edit-barbershop-location')
            barbershop_phone_number = request.form.get('edit-barbershop-phone-number')
            file = request.files['edit-barbershop-picture']
            cur.execute("SELECT * FROM barbershops WHERE barbershop_id = %s", (barbershop_id,))
            result = cur.fetchone()
            print(f'results: {result}')
            fields_to_update = {}
            if barbershop_name and barbershop_name != result[2]:
                fields_to_update['barbershop_name'] = barbershop_name
            if barbershop_location and barbershop_location != result[4]:
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
                        print(clause)
                        query = f"UPDATE barbershops SET {clause} WHERE barbershop_id = %s"
                        print(query)
                        values = list(fields_to_update.values()) + [barbershop_id]
                        print(values)
                        cur.execute(query, values)
                        connection.commit()
                        return redirect(url_for('views.admin'))
                except Exception as e:
                    print(f'an error has occurred while updating barbershop information, {e}')
            else:
                print('no changes were made')
    return render_template("admin.html")
