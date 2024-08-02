from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify as flask_jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, login_manager
import psycopg2
from .models import connection, User

auth = Blueprint("auth", __name__)
cur = connection.cursor()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form.get('email_or_phone')
        password = request.form.get('password')
        remember = request.form.get('remember')

        email = ""
        phone_number = ""
        if '@' in email_or_phone:
            email = email_or_phone
        else:
            phone_number = email_or_phone

        if remember == 'on':
            remember_status = True
        else:
            remember_status = False
        try:
            with connection.cursor() as cur:

                if email:
                    # Check if the email corresponds to an owner
                    cur.execute("SELECT * FROM users WHERE email = %s AND is_owner = true", (email,))
                else:
                    # Check if the phone number corresponds to an owner
                    cur.execute("SELECT * FROM users WHERE phone_number = %s AND is_owner = true", (phone_number,))

                admin = cur.fetchone()
                if admin:
                    admin_user = User(*admin)
                    if check_password_hash(admin_user.password, password):
                        login_user(admin_user, remember=remember_status)
                        return redirect(url_for('views.admin'))
                    else:
                        flash('Incorrect email, phone number or password, try again', category='error')
                if email:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                else:
                    cur.execute("SELECT * FROM users WHERE phone_number = %s", (phone_number,))
                user_data = cur.fetchone()
                if user_data:
                    user = User(*user_data)
                    if check_password_hash(user.password, password):
                        flash('Logged in successfully', category='success')
                        login_user(user, remember=remember_status)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Incorrect email, phone number or password, try again', category='error')
                else:
                    flash('Incorrect email, phone number or password, try again', category='error')
        except Exception as e:
            flash(f"An error has occurred: {e}")
    return render_template("login.html", user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email_or_phone = request.form.get('email_or_phone')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        remember = request.form.get('remember') == 'on'

        email = ""
        phone_number = ""
        if '@' in email_or_phone:
            email = email_or_phone
        else:
            phone_number = email_or_phone

        try:
            with connection.cursor() as cur:
                # Check if email or phone number already exists
                if email:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                    email_user = cur.fetchone()
                else:
                    email_user = None

                if phone_number:
                    cur.execute("SELECT * FROM users WHERE phone_number = %s", (phone_number,))
                    phone_user = cur.fetchone()
                else:
                    phone_user = None

                if email_user or phone_user:
                    flash('Email or phone number already exists', category='error')
                elif len(first_name) < 3:
                    flash('Too short first name', category='error')
                elif email and len(email) < 6:
                    flash('Invalid email', category='error')
                elif phone_number and len(phone_number) < 6:
                    flash('Invalid phone number', category='error')
                elif password1 != password2:
                    flash("Passwords don't match", category='error')
                elif len(password1) < 4:
                    flash('Password length should be at least 4', category='error')
                else:
                    # Insert new user into the database
                    password = generate_password_hash(password1, method='pbkdf2:sha256')
                    if email and phone_number:
                        cur.execute(
                            """INSERT INTO users (first_name, last_name, email, phone_number, password) VALUES (%s, %s, %s, %s, %s)
                            RETURNING id""",
                            (first_name, last_name, email, phone_number, password)
                        )
                    elif email:
                        cur.execute(
                            """INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)
                            RETURNING id""",
                            (first_name, last_name, email, password)
                        )
                    elif phone_number:
                        cur.execute(
                            """INSERT INTO users (first_name, last_name, phone_number, password) VALUES (%s, %s, %s, %s)
                            RETURNING id""",
                            (first_name, last_name, phone_number, password)
                        )
                    user_id = cur.fetchone()
                    connection.commit()

                    # Retrieve the newly created user from the database
                    new_user = User.get(user_id)
                    if new_user:
                        login_user(new_user, remember=remember)
                        flash('Account created', category='success')
                        return redirect(url_for('views.home'))
                    else:
                        flash('An error occurred while creating your account. Please try again.', category='error')
        except Exception as e:
            connection.rollback()  # Rollback the transaction if an error occurs
            flash(f"An error has occurred: {e}", category='error')

    return render_template("register.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('delete-account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    print(user_id)
    if current_user.id != user_id:
        return 'Unauthorized', 403
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (current_user.id,))
            connection.commit()
        logout_user()
        return flask_jsonify(success=True, message="Account successfully deleted"), 200
    except Exception as e:
        connection.rollback()
        return flask_jsonify(success=False, message=f"An error occurred while deleting account: {e}"), 500