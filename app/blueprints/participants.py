from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

participants = Blueprint('participants', __name__)

# Route to display all participants
@participants.route('/participants')
def show_participants():
    connection = get_db()
    query = "SELECT * FROM participants"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert fetched data to a Pandas DataFrame
    df = pd.DataFrame(result, columns=['participant_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'contact_info'])

    # Optional: Add a full name column for demonstration purposes
    df['full_name'] = df['first_name'] + ' ' + df['last_name']

    # Convert the DataFrame back to a list of dictionaries for rendering in the template
    all_participants = df.to_dict('records')

    return render_template("participants.html", participants=all_participants)

# Route to add a participant
@participants.route('/participants/add', methods=['POST'])
def add_participant():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    contact_info = request.form.get('contact_info', '')

    connection = get_db()
    query = "INSERT INTO participants (first_name, last_name, date_of_birth, gender, contact_info) VALUES (%s, %s, %s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(query, (first_name, last_name, date_of_birth, gender, contact_info))
    connection.commit()
    flash("Participant added successfully!", "success")
    return redirect(url_for('participants.show_participants'))

# Route to edit a participant
@participants.route('/participants/edit/<int:participant_id>', methods=['POST'])
def edit_participant(participant_id):
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    contact_info = request.form['contact_info']

    connection = get_db()
    query = "UPDATE participants SET first_name=%s, last_name=%s, date_of_birth=%s, gender=%s, contact_info=%s WHERE participant_id=%s"
    with connection.cursor() as cursor:
        cursor.execute(query, (first_name, last_name, date_of_birth, gender, contact_info, participant_id))
    connection.commit()
    flash("Participant updated successfully!", "success")
    return redirect(url_for('participants.show_participants'))

# Route to delete a participant
@participants.route('/participants/delete/<int:participant_id>', methods=['POST'])
def delete_participant(participant_id):
    connection = get_db()
    query = "DELETE FROM participants WHERE participant_id=%s"
    with connection.cursor() as cursor:
        cursor.execute(query, (participant_id,))
    connection.commit()
    flash("Participant deleted successfully!", "success")
    return redirect(url_for('participants.show_participants'))
