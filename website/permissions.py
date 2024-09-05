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
        results_html = ''
        if search_results:
            for result in search_results:
                barbershop_id = result[0]
                with connection.cursor() as cur:
                    cur.execute("SELECT * FROM barbers WHERE barbershop_id = %s", (barbershop_id,))
                    barbers = cur.fetchall()
                    #print(f"barber results: {barbers}")
                    barber_info_html = ""
                    barber_delete_html = ""
                    barber_names_html = '<option value="" disabled selected>Select a barber</option>'
                    for barber in barbers:
                        with connection.cursor() as cur:
                            cur.execute("""
                            SELECT DISTINCT b.barber_id, h.haircut_id, h.haircut_name,
                                h.price,  h.description
                                FROM barbers b
                                JOIN  barber_haircuts bh ON b.barber_id = bh.barber_id 
                                JOIN haircuts h ON h.haircut_id = bh.haircut_id
                                JOIN barbershops bs ON b.barbershop_id = bs.barbershop_id
                                WHERE bs.barbershop_id = %s AND b.barber_id = %s  AND TRIM(h.haircut_name) <> '';
                            """, (barbershop_id, barber[0]))
                            haircuts = cur.fetchall()
                            #print(f"haircuts: {haircuts}")
                            haircut_list_html = ""
                            for haircut in haircuts:
                                haircut_list_html += f'''
                               <div class="input-group mb-3">
                                    <input type="text" class="form-control-settings" name="edit-barber-haircut_name[]" value="{haircut[2]}">
                                    <input type="number" class="form-control-settings" name="edit-barber-haircut_price[]" value="{haircut[3]}" style="width: 70%;">
                                    <input type="text" class="form-control-settings" name="edit-barber-haircut_description[]" value="{haircut[4]}">
                                    <div class="input-group-append">
                                        <button class="btn btn-outline-secondary remove-haircut-btn" type="button">-</button>
                                    </div>
                                </div>
                            '''

                        barber_names_html += f'<option value="{barber[0]}">{barber[2]} {barber[3]}</option>'
                        barber_delete_html += f'''
                            <div id="barber-delete-container-{barber[0]}" class="barber-delete-container" style="display: none;">
                                <div class="delete-barber-container">
                                    <input type="hidden" name="barber_id_delete id="barber-id-delete" value="{barber[0]}">
                                    <button type="button" id="delete-barber-btn" class="delete-barber-btn" data-barber-id="{barber[0]}" style="margin-top: 40px; margin-left: 10px;">Delete barber '{barber[2]}'</button> 
                                    <p>Note that after deleting this barber his/her all data in the system will be <strong>deleted permanently.</strong></p>
                                </div>
                            </div>
                        '''
                        barber_info_html += f'''
                            <div id="barber-info-container-{barber[0]}" class="barber-info-container" style="display: none;">
                                <div class="settings-edit-barbers-content">
                                <input type="hidden" name="barber_id_hidden" value="{barber[0]}">
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-first-name">Barber first name</label>
                                                <input type="text" class="form-control-settings" id="settings-edit-barber-first-name" name="settings-edit-barber-first-name" value={barber[2]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-last-name">Barber last name</label>
                                                <input type="text" class="form-control-settings" id="settings-edit-barber-last-name" name="settings-edit-barber-last-name" value={barber[3]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-phone-number">Barber phone number</label>
                                                <input type="tel" class="form-control-settings" id="settings-edit-barber-phone-number" name="settings-edit-barber-phone-number" value={barber[4]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-email">Barber email</label>
                                                <input type="email" class="form-control-settings" id="settings-edit-barber-email" name="settings-edit-barber-email" value={barber[7]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-experienced-years">Experienced years</label>
                                                <input type="number" class="form-control-settings" id="settings-edit-barber-experienced-years" name="settings-edit-barber-experienced-years" value={barber[8]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-working-start-time">Working start time</label>
                                                <input type="time" class="form-control-settings" id="settings-edit-barber-working-start-time" name="settings-edit-barber-working-start-time" value={barber[9]}>
                                            </div> 
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-working-end-time">Working end time</label>
                                                <input type="time" class="form-control-settings" id="settings-edit-barber-working-end-time" name="settings-edit-barber-working-end-time" value={barber[10]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-break-start-time">Break start time</label>
                                                <input type="time" class="form-control-settings" id="settings-edit-barber-break-start-time" name="settings-edit-barber-break-start-time" value={barber[11]}>
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-break-end-time">Break end time</label>
                                                <input type="time" class="form-control-settings" id="settings-edit-barber-break-end-time" name="settings-edit-barber-break-end-time" value={barber[12]}>
                                            </div>
                                            
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-working-days">Working days</label>
                                                <div id="settings-edit-barber-working-days" name="settings-edit-barber-working-days" style="margin-top: 20px;">
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="monday" name="edit-working-days" value="Monday">
                                                        <label for="monday">Monday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="tuesday" name="edit-working-days" value="Tuesday">
                                                        <label for="tuesday">Tuesday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="wednesday" name="edit-working-days" value="Wednesday">
                                                        <label for="wednesday">Wednesday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="thursday" name="edit-working-days" value="Thursday">
                                                        <label for="thursday">Thursday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="friday" name="edit-working-days" value="Friday">
                                                        <label for="friday">Friday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="saturday" name="edit-working-days" value="Saturday">
                                                        <label for="saturday">Saturday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="sunday" name="edit-working-days" value="Sunday">
                                                        <label for="sunday">Sunday</label>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                           <div class="form-group-settings">
                                                <label for="settings-edit-barber-skills">Skills (Haircuts)</label>
                                                <div id="haircut-container-{barber[0]}">
                                                    {haircut_list_html}
                                                    <div class="input-group mb-3">
                                                        <input type="text" class="form-control-settings" name="edit-barber-haircut_name[]" placeholder="Haircut">
                                                        <input type="number" class="form-control-settings" name="edit-barber-haircut_name[]" placeholder="Price" style="width: 70%;">
                                                        <input type="text" class="form-control-settings" name="edit-barber-haircut_description[]" placeholder="Description">
                                                        <div class="input-group-append">
                                                            <button class="btn btn-outline-secondary add-haircut-btn" type="button">+</button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber-picture">Barber picture</label>
                                                <input type="file" class="form-control-settings" id="settings-edit-barber-picture" name="settings-edit-barber-picture">
                                            </div>
                                        </div>
                                </div> 
                            
                        '''


                # results_html += f'<div class="search-result-item" data-id="{result[0]}">{result[1]}, Location: {result[2]} <button class="btn btn-link p-0" id="toggle-search-results-btn1"><i class="fas fa-plus"></i></button></div>'
                results_html += f'''
        <div class="search-result-item" data-id="{result[0]}">
                    <div class="results-header" style="display: flex; justify-content: space-between;">
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
                                    <input type="text" class="form-control" id="edit-barbershop-name" name="edit-barbershop-name" value="{result[1]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-location">Barbershop location</label>
                                    <input type="text" class="form-control" id="edit-barbershop-location" name="edit-barbershop-location"
                                     value="{result[2]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-phone-number">Barbershop owner's phone number</label>
                                     <input type="tel" class="form-control" id="edit-barbershop-phone-number" name="edit-barbershop-phone-number" value="{result[3]}">
                                </div>
                                <div class="form-group">
                                    <label for="barbershop-picture">Barbershop picture</label>
                                    <input type="file" class="form-control" id="edit-barbershop-picture" name="edit-barbershop-picture">
                                </div>
                            <input type="hidden" name="barbershop_id" value="{result[0]}">
                            
                            <div class="edit-barbershop-settings-container">
                                <div class="edit-settings-header">
                                    <button type="button" class="toggle-edit-barbershop-settings-btn">
                                        Edit Barbershop Settings <i class="fas fa-plus"></i>
                                     </button>
                                </div>
                                <div class="edit-settings-content" style="display: none;">
                                
                                    <div class="settings-add-barbers-container">
                                        <div class="settings-add-barbers-header">
                                            <button type="button" class="toggle-add-barbers-btn">
                                                Add barbers <i class="fas fa-plus"></i>
                                            </button>    
                                        </div>
                                        
                                        <div class="settings-add-barbers-content" style="display: none;">
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-first-name">Barber first name</label>
                                                <input type="text" class="form-control-settings" id="settings-add-barber-first-name" name="settings-add-barber-first-name">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-last-name">Barber last name</label>
                                                <input type="text" class="form-control-settings" id="settings-add-barber-last-name" name="settings-add-barber-last-name">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-phone-number">Barber phone number</label>
                                                <input type="tel" class="form-control-settings" id="settings-add-barber-phone-number" name="settings-add-barber-phone-number" >
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-email">Barber email</label>
                                                <input type="email" class="form-control-settings" id="settings-add-barber-email" name="settings-add-barber-email">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-experienced-years">Experienced years</label>
                                                <input type="number" class="form-control-settings" id="settings-add-barber-experienced-years" name="settings-add-barber-experienced-years">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-working-start-time">Working start time</label>
                                                <input type="time" class="form-control-settings" id="settings-add-barber-working-start-time" name="settings-add-barber-working-start-time">
                                            </div> 
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-working-end-time">Working end time</label>
                                                <input type="time" class="form-control-settings" id="settings-add-barber-working-end-time" name="settings-add-barber-working-end-time">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-break-start-time">Break start time</label>
                                                <input type="time" class="form-control-settings" id="settings-add-barber-break-start-time" name="settings-add-barber-break-start-time">
                                            </div>
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-break-end-time">Break end time</label>
                                                <input type="time" class="form-control-settings" id="settings-add-barber-break-end-time" name="settings-add-barber-break-end-time">
                                            </div>
                                            
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-working-days">Working days</label>
                                                <div id="settings-add-barber-working-days" name="settings-add-barber-working-days" style="margin-top: 20px;">
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="monday" name="working_days" value="Monday">
                                                        <label for="monday">Monday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="tuesday" name="working_days" value="Tuesday">
                                                        <label for="tuesday">Tuesday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="wednesday" name="working_days" value="Wednesday">
                                                        <label for="wednesday">Wednesday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="thursday" name="working_days" value="Thursday">
                                                        <label for="thursday">Thursday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="friday" name="working_days" value="Friday">
                                                        <label for="friday">Friday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="saturday" name="working_days" value="Saturday">
                                                        <label for="saturday">Saturday</label>
                                                    </div>
                                                    <div class="custom-checkbox">
                                                        <input type="checkbox" id="sunday" name="working_days" value="Sunday">
                                                        <label for="sunday">Sunday</label>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-skills">Skills (Haircuts)</label>
                                                <div id="haircut-container">
                                                    <div class="input-group mb-3">
                                                        <input type="text" class="form-control-settings" name="haircut_name[]" placeholder="Haircut">
                                                        <input type="number" class="form-control-settings" name="haircut_price[]" placeholder="Price" style="width: 70%;">
                                                        <input type="text" class="form-control-settings" name="haircut_description[]" placeholder="Description(optional)">
                                                        <div class="input-group-append">
                                                            <button class="btn btn-outline-secondary add-haircut-btn" type="button">+</button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="form-group-settings">
                                                <label for="settings-add-barber-picture">Barber picture(optional)</label>
                                                <input type="file" class="form-control-settings" id="settings-add-barber-picture" name="settings-add-barber-picture">
                                            </div>
                                        </div>
                                    </div>
                                    
                                    
                                    <div class="settings-edit-barbers-container">
                                        <div class="settings-edit-barbers-header">
                                            <button type="button" class="toggle-edit-barbers-btn">
                                                Edit barbers <i class="fas fa-plus"></i>
                                            </button>    
                                        </div>
                                        
                                        <div class="settings-edit-barbers-content" id="settings-edit-barbers-content" style="display: none;">
                                            <div class="form-group-settings">
                                                <label for="settings-edit-barber">Barber name</label>
                                                <select id="settings-edit-barber" class="styled-select-barbers" name="select-settings-edit-barber">
                                                    {barber_names_html}  <!-- Inject barber options here -->
                                                </select>
                                            </div>
                                            
                                            
                                            {barber_info_html}
                                            
                                            
                                        </div>
                                    </div>
                                    
                                    
                                    <div class="settings-delete-barbers-container">
                                        <div class="settings-delete-barbers-header">
                                            <button type="button" class="toggle-delete-barbers-btn">
                                                Delete barbers <i class="fas fa-plus"></i>
                                            </button>    
                                        </div>
                                        
                                        <div class="settings-delete-barbers-content" style="display: none;">
                                           <div class="form-group-settings">
                                                <label for="settings-delete-barber">Barber name</label>
                                                <select id="settings-delete-barber" class="styled-select-to-delete-barbers" name="select-settings-edit-barber">
                                                    {barber_names_html}  <!-- Inject barber options here -->
                                                </select>
                                            </div>
                                            
                                            {barber_delete_html}
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
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
        barbershop_id = request.form.get('barbershop_id')

        with connection.cursor() as cur:
            settings_add_barber_first_name = request.form.get('settings-add-barber-first-name')
            #print(f"adding first name: {settings_add_barber_first_name}")
            settings_add_barber_last_name = request.form.get('settings-add-barber-last-name')
            #print(f"adding last name: {settings_add_barber_last_name}")
            settings_add_barber_phone_number = request.form.get('settings-add-barber-phone-number')
            #print(f"adding phone number: {settings_add_barber_phone_number}")
            settings_add_barber_email = request.form.get('settings-add-barber-email')
            #print(f"adding email: {settings_add_barber_email}")
            settings_add_barber_experienced_years = request.form.get('settings-add-barber-experienced-years')
            #print(f"adding experienced years: {settings_add_barber_experienced_years}")
            settings_add_barber_working_start_time = request.form.get('settings-add-barber-working-start-time')
            #print(f"adding working start time: {settings_add_barber_working_start_time}")
            settings_add_barber_working_end_time = request.form.get('settings-add-barber-working-end-time')
            #print(f"adding working end time: {settings_add_barber_working_end_time}")
            settings_add_barber_break_start_time = request.form.get('settings-add-barber-break-start-time')
            #print(f"adding break start time: {settings_add_barber_break_start_time}")
            settings_add_barber_break_end_time = request.form.get('settings-add-barber-break-end-time')
            #print(f"adding break end time: {settings_add_barber_break_end_time}")
            settings_add_barber_working_days = request.form.getlist('working_days')
            settings_add_barber_picture = request.files['settings-add-barber-picture']
            haircut_name = request.form.getlist('haircut_name[]')
            haircut_price = request.form.getlist('haircut_price[]')
            haircut_description = request.form.getlist('haircut_description[]')
            skills = []
            for name, price, description in zip(haircut_name, haircut_price, haircut_description):
                skills.append({
                    'haircut_name': name,
                    'haircut_price': price,
                    'description': description
                })
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
                add_query = f"INSERT INTO barbers ({column}, barbershop_id, password) VALUES ({placeholders}, %s, %s)"
                add_values = list(fields_to_add.values())
                add_values.append(barbershop_id)
                add_values.append(password)
                cur.execute(add_query, add_values)
                cur.execute("SELECT barber_id FROM barbers ORDER BY created_date DESC")
                barber_id = cur.fetchone()[0]
                cur.execute("""INSERT INTO users(first_name, last_name, email, phone_number, password, profile_picture, is_barber, barber_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (fields_to_add['barber_first_name'], fields_to_add['barber_last_name'],
                    fields_to_add['barber_email'], fields_to_add['barber_phone_number'], password, fields_to_add['barber_picture'], 'true', barber_id
                )) # GO BACK HERE
                for values in skills:
                    barber_query = f"INSERT INTO haircuts(haircut_name, price, description, barbershop_id) VALUES(%s, %s, %s ,%s) RETURNING haircut_id"
                    cur.execute(barber_query,
                                (values['haircut_name'], values['haircut_price'], values['description'], barbershop_id))
                    haircut_id = cur.fetchone()
                    insert_query = "INSERT INTO barber_haircuts(barber_id, haircut_id) VALUES(%s, %s)"
                    cur.execute(insert_query, (barber_id, haircut_id))
                    print(f"barber added successfully")
                    connection.commit()

        with connection.cursor() as cur:
            settings_edit_barber_first_name = request.form.get('settings-edit-barber-first-name')
            #print(f"editing barber first name: {settings_edit_barber_first_name}")
            settings_edit_barber_last_name = request.form.get('settings-edit-barber-last-name')
            #print(f"editing barber last name: {settings_edit_barber_last_name}")
            settings_edit_barber_phone_number = request.form.get('settings-edit-barber-phone-number')
            #print(f"editing barber phone number: {settings_edit_barber_phone_number}")
            settings_edit_barber_email = request.form.get('settings-edit-barber-email')
            #print(f"editing barber email: {settings_edit_barber_email}")
            settings_edit_barber_experienced_years = request.form.get('settings-edit-barber-experienced-years')
            #print(f"editing barber experienced years: {settings_edit_barber_experienced_years}")
            settings_edit_barber_working_start_time = request.form.get('settings-edit-barber-working-start-time')
            #print(f"editing barber working start time: {settings_edit_barber_working_start_time}")
            settings_edit_barber_working_end_time = request.form.get('settings-edit-barber-working-end-time')
            #print(f"editing barber working end time: {settings_edit_barber_working_end_time}")
            settings_edit_barber_break_start_time = request.form.get('settings-edit-barber-break-start-time')
            #print(f"editing barber break start time: {settings_edit_barber_break_start_time}")
            settings_edit_barber_break_end_time = request.form.get('settings-edit-barber-break-end-time')
            #print(f"editing barber break end time: {settings_edit_barber_break_end_time}")
            settings_edit_barber_working_days = request.form.getlist('edit-working-days')
            settings_edit_haircut_name = request.form.getlist('edit-barber-haircut_name[]')
            print(settings_edit_haircut_name)
            settings_edit_haircut_price = request.form.getlist('edit-barber-haircut_price[]')
            print(settings_edit_haircut_price)
            settings_edit_haircut_description = request.form.getlist('edit-barber-haircut_description[]')
            print(settings_edit_haircut_description)
            settings_edit_barber_picture = request.files.get('settings-edit-barber-picture')
            edit_skills = []
            for edit_name, edit_price, edit_description in zip(settings_edit_haircut_name, settings_edit_haircut_price, settings_edit_haircut_description):
                edit_skills.append({
                    'haircut_name': edit_name,
                    'price': edit_price,
                    'description': edit_description
                })
            print(f'debug edit haircut name: {settings_edit_haircut_name}')
            print(f'debug edit haircut price: {settings_edit_haircut_price}')
            print(f'debug edit description: {settings_edit_haircut_description}')
            print(f"debug edit skills: {edit_skills}")
            if settings_edit_barber_first_name or settings_edit_barber_last_name or settings_edit_barber_phone_number or settings_edit_barber_email or settings_edit_barber_experienced_years or settings_edit_barber_working_start_time or settings_edit_barber_working_end_time or settings_edit_barber_break_start_time or settings_edit_barber_break_end_time or settings_edit_barber_working_days or settings_edit_barber_picture:

                fields_to_edit = {}

                barber_id = request.form.get('barber_id_hidden')
                cur.execute("SELECT * FROM barbers WHERE barber_id = %s", (barber_id,))
                result = cur.fetchone()
               # print(f"results barber id: {barber_id}, results: {result}")
                if settings_edit_barber_first_name and settings_edit_barber_first_name != result[2]:
                    fields_to_edit['barber_first_name'] = settings_edit_barber_first_name
                if settings_edit_barber_last_name and settings_edit_barber_last_name != result[3]:
                    fields_to_edit['barber_last_name'] = settings_edit_barber_last_name
                if settings_edit_barber_phone_number and settings_edit_barber_phone_number != result[4]:
                    fields_to_edit['barber_phone_number'] = settings_edit_barber_phone_number
                if settings_edit_barber_email and settings_edit_barber_email != result[7]:
                    fields_to_edit['barber_email'] = settings_edit_barber_email
                if settings_edit_barber_experienced_years and settings_edit_barber_experienced_years != result[8]:
                    fields_to_edit['experienced_years'] = settings_edit_barber_experienced_years
                if settings_edit_barber_working_start_time and settings_edit_barber_working_start_time != result[9]:
                    fields_to_edit['working_start_time'] = settings_edit_barber_working_start_time
                if settings_edit_barber_working_end_time and settings_edit_barber_working_end_time != result[10]:
                    fields_to_edit['working_end_time'] = settings_edit_barber_working_end_time
                if settings_edit_barber_break_start_time and settings_edit_barber_break_start_time != result[11]:
                    fields_to_edit['break_start_time'] = settings_edit_barber_break_start_time
                if settings_edit_barber_break_end_time and settings_edit_barber_break_end_time != result[12]:
                    fields_to_edit['break_end_time'] = settings_edit_barber_break_end_time
                if settings_edit_barber_working_days:
                    fields_to_edit['working_days'] = ', '.join(settings_edit_barber_working_days)

                if settings_edit_barber_picture:
                    filename = secure_filename(settings_edit_barber_picture.filename)
                    current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
                    picture_upload_folder = current_app.config['UPLOAD_FOLDER']
                    picture_file_path = os.path.join(picture_upload_folder, filename)

                    if not os.path.exists(picture_upload_folder):
                        os.makedirs(picture_upload_folder)
                    try:
                        settings_edit_barber_picture.save(picture_file_path)
                        try:
                            with open(picture_file_path, 'rb') as f:
                                binary_data = f.read()
                                picture = psycopg2.Binary(binary_data)
                                fields_to_edit['barber_picture'] = picture
                        except Exception as e:
                            print(f"An error has occurred while saving a file")
                    except Exception as e:
                        print(f"An error has occurred while storing a file")
                if fields_to_edit or edit_skills:
                    try:
                        # Update barber information
                        if fields_to_edit:
                            clause = ', '.join(f"{field} = %s" for field in fields_to_edit)
                            query = f"UPDATE barbers SET {clause} WHERE barbershop_id = %s AND barber_id = %s RETURNING barber_id"
                            values = list(fields_to_edit.values()) + [barbershop_id, barber_id]
                            cur.execute(query, values)

                        # Fetch existing haircuts for this barber
                        cur.execute(
                            "SELECT h.haircut_id FROM haircuts h JOIN barber_haircuts bh ON h.haircut_id = bh.haircut_id WHERE bh.barber_id = %s",
                            (barber_id,))
                        existing_haircuts = set(row[0] for row in cur.fetchall())
                        print(f"values: {edit_skills}")
                        for values in edit_skills:
                            # Insert haircuts for the barber
                            barber_query = """
                                INSERT INTO haircuts (haircut_name, price, description, barbershop_id)
                                VALUES (%s, %s, %s, %s)
                                RETURNING haircut_id
                            """
                            cur.execute(barber_query,
                                        (values['haircut_name'], values['price'], values['description'], barbershop_id))
                            haircut_id = cur.fetchone()[0]
                            connection.commit()
                            # Associate the inserted haircut with the barber
                            insert_query = """
                                INSERT INTO barber_haircuts (barber_id, haircut_id)
                                VALUES (%s, %s)
                            """
                            cur.execute(insert_query, (barber_id, haircut_id))

                            connection.commit()




                        print("Barber and haircuts updated successfully")
                    except Exception as e:
                        print(f'An error occurred while updating barber information: {e}')
                        connection.rollback()
                else:
                    print('No changes were made')

        with connection.cursor() as cur:
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
                    <div class="delete-search-result-content" style="display: none;">
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
    data = request.get_json()  # Get the JSON data sent from the frontend
    barber_id = data.get('barber_id')  # Access the barber_name variable
    print(f"barber id from frontend: {barber_id}")
    with connection.cursor() as cur:
        cur.execute("DELETE FROM barbers WHERE barber_id = %s", (barber_id,))
        cur.execute("SELECT haircut_id FROM barber_haircuts WHERE barber_id = %s", (barber_id,))
        haircuts_id = cur.fetchall()
        cur.execute("DELETE FROM barber_haircuts WHERE barber_id = %s", (barber_id,))
        for haircut_id in haircuts_id:
            cur.execute("DELETE FROM haircuts WHERE haircut_id = %s", (haircut_id,))
        cur.execute("UPDATE appointments SET is_active  = false WHERE barber_id = %s", (barber_id,))
        connection.commit()
    return flask_jsonify({'success': True})


@permissions.route('/delete_barbershop', methods=['POST'])
@login_required
def delete_barbershop():
    if request.method == 'POST':
        barbershop_id = request.form.get('barbershop_id_to_delete')
        with connection.cursor() as cur:
            cur.execute("DELETE FROM barbershops WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("UPDATE barbers SET barbershop_id = NULL WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("UPDATE haircuts SET barbershop_id = NULL WHERE barbershop_id = %s", (barbershop_id,))
            cur.execute("UPDATE appointments SET is_active = false WHERE barbershop_id = %s", (barbershop_id,))
            connection.commit()
        return redirect(url_for('views.admin'))


@permissions.route('/add-appointment', methods=['POST'])
@login_required
def add_appointment():
    barbershop_name = request.form.get('add-appointment-barbershop-name')
    barber_name = request.form.get('barber-name')
    customer_first_name = request.form.get('customer-first-name')
    customer_last_name = request.form.get('customer-last-name')
    customer_phone_number = request.form.get('customer-phone-number')
    haircut_name = request.form.get('haircut-select')
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
        cur.execute("""
            SELECT barbershop_id FROM barbershops WHERE barbershop_name ILIKE %s
        """, (barbershop_name,))
        barbershop_id = cur.fetchone()

        cur.execute("""
            SELECT barber_id FROM barbers WHERE barber_first_name ILIKE %s
        """, (barber_name,))
        barber_id = cur.fetchone()

        cur.execute("""
            SELECT haircut_id FROM haircuts WHERE haircut_name ILIKE %s
        """, (haircut_name,))
        haircut_id = cur.fetchone()

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


@permissions.route('/get-all-haircuts', methods=['GET'])
def get_all_haircuts():
    barber_id = session.get('add-appointment-barber-id')
    cur.execute("""
        SELECT DISTINCT h.haircut_name, h.price
        FROM haircuts h
        JOIN barber_haircuts bs ON h.haircut_id = bs.haircut_id
        WHERE bs.barber_id = %s
    """, (barber_id,))
    results = cur.fetchall()
    return flask_jsonify([{"haircut_name": result[0], "price": result[1]} for result in results])


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


@permissions.route('/list-appointments', methods=['GET'])
@login_required
def list_appointments():
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
            ORDER BY appointment_date, appointment_time
        ''')
        appointments = cur.fetchall()
        print(f"appointments: {appointments}")

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


@permissions.route('/delete-appointment', methods=['POST'])
@login_required
def delete_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        with connection.cursor() as cur:
            print(f"appointment_id: {appointment_id}")
            cur.execute("DELETE FROM appointments WHERE appointment_id = %s", (appointment_id,))
            connection.commit()
            return redirect(url_for('views.admin'))


@permissions.route('/get-available-dates', methods=['GET'])
def get_available_dates():
    barbershop_id = session.get('send_barbershop_id')
    barber_id = session.get('add-appointment-barber-id')
    available_dates = days(barber_id, barbershop_id)
    return flask_jsonify({'available_dates': available_dates})


# Route to get available times for a selected barber on a specific day
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

    cur.execute("SELECT appointment_time FROM appointments WHERE barber_id = %s AND appointment_date = %s",
                (barber_id, day))
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
