from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db

trials = Blueprint('trials', __name__)

# Route to display all trials
@trials.route('/trials')
def show_trials():
    connection = get_db()
    query = "SELECT trial_id, trial_name, start_date, end_date, status FROM trials"
    with connection.cursor() as cursor:
        cursor.execute(query)
        trials = cursor.fetchall()

    # Fetch participants for the dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()

    return render_template("trials.html", trials=trials, participants=participants)

# Route to add a trial
@trials.route('/trials/add', methods=['POST'])
def add_trial():
    trial_name = request.form['trial_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    status = request.form['status']
    participant_id = request.form['participant_id']

    connection = get_db()
    query = "INSERT INTO trials (trial_name, start_date, end_date, status, participant_id) VALUES (%s, %s, %s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(query, (trial_name, start_date, end_date, status, participant_id))
    connection.commit()
    flash("Trial added successfully!", "success")
    return redirect(url_for('trials.show_trials'))

# Route to edit a trial
@trials.route('/trials/edit/<int:trial_id>', methods=['POST'])
def edit_trial(trial_id):
    trial_name = request.form['trial_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    status = request.form['status']

    connection = get_db()
    query = """
        UPDATE trials
        SET trial_name = %s, start_date = %s, end_date = %s, status = %s
        WHERE trial_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (trial_name, start_date, end_date, status, trial_id))
    connection.commit()
    flash("Trial updated successfully!", "success")
    return redirect(url_for('trials.show_trials'))

# Route to delete a trial
@trials.route('/trials/delete/<int:trial_id>', methods=['POST'])
def delete_trial(trial_id):
    connection = get_db()
    query = "DELETE FROM trials WHERE trial_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (trial_id,))
    connection.commit()
    flash("Trial deleted successfully!", "success")
    return redirect(url_for('trials.show_trials'))