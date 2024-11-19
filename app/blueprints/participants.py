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

    # Convert result to Pandas DataFrame
    df = pd.DataFrame(result,
                      columns=['participant_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'contact_info'])

    # Add action buttons for editing and deleting
    df['Actions'] = df['participant_id'].apply(lambda p_id:
                                               f'<a href="{url_for("participants.edit_participant", participant_id=p_id)}" class="btn btn-sm btn-info">Edit</a> '
                                               f'<form action="{url_for("participants.delete_participant", participant_id=p_id)}" method="post" style="display:inline;">'
                                               f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                               )

    # Convert DataFrame to HTML for display
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("participants/participants.html", table=rows_only)


# Route to add a new participant
@participants.route('/participants/add', methods=['GET', 'POST'])
def add_participant():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        contact_info = request.form['contact_info']

        connection = get_db()
        query = "INSERT INTO participants (first_name, last_name, date_of_birth, gender, contact_info) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (first_name, last_name, date_of_birth, gender, contact_info))
        connection.commit()
        flash("New participant added successfully!", "success")
        return redirect(url_for('participants.show_participants'))

    return render_template("participants/add_participant.html")


# Route to edit an existing participant
@participants.route('/participants/edit/<int:participant_id>', methods=['GET', 'POST'])
def edit_participant(participant_id):
    connection = get_db()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        contact_info = request.form['contact_info']

        query = """
            UPDATE participants 
            SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, contact_info = %s 
            WHERE participant_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (first_name, last_name, date_of_birth, gender, contact_info, participant_id))
        connection.commit()
        flash("Participant data updated successfully!", "success")
        return redirect(url_for('participants.show_participants'))

    # Fetch participant data for editing
    query = "SELECT * FROM participants WHERE participant_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (participant_id,))
        participant = cursor.fetchone()

    return render_template("participants/edit_participant.html", participant=participant)


# Route to delete a participant
@participants.route('/participants/delete/<int:participant_id>', methods=['POST'])
def delete_participant(participant_id):
    connection = get_db()
    query = "DELETE FROM participants WHERE participant_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (participant_id,))
    connection.commit()
    flash("Participant deleted successfully!", "success")
    return redirect(url_for('participants.show_participants'))
