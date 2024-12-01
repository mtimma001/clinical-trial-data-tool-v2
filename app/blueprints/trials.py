from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

from app.functions import prepare_visualization_data

trials = Blueprint('trials', __name__)

# Route to display all trials
@trials.route('/trials')
def show_trials():
    connection = get_db()
    query = """
        SELECT t.trial_id, t.trial_name, t.start_date, t.end_date, t.status
        FROM trials t
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert result to Pandas DataFrame
    df = pd.DataFrame(result, columns=['trial_id', 'trial_name', 'start_date', 'end_date', 'status'])

    # Add action buttons for editing and deleting
    df['Actions'] = df['trial_id'].apply(lambda t_id:
                                         f'<a href="{url_for("trials.edit_trial", trial_id=t_id)}" class="btn btn-sm btn-warning">Edit</a> '
                                         f'<form action="{url_for("trials.delete_trial", trial_id=t_id)}" method="post" style="display:inline;">'
                                         f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                         )

    # Convert DataFrame to HTML for display
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("trials/trials.html", table=rows_only)

# Route to add a new trial
@trials.route('/trials/add', methods=['GET', 'POST'])
def add_trial():
    connection = get_db()
    if request.method == 'POST':
        trial_name = request.form['trial_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']
        participant_id = request.form['participant_id']
        print(participant_id)

        # Ensure participant_id is valid
        with connection.cursor() as cursor:
            cursor.execute("SELECT participant_id FROM participants WHERE participant_id = %s", (participant_id,))
            participant = cursor.fetchone()
            print(participant)
            if not participant:
                flash("Invalid participant ID", "danger")
                return redirect(url_for('trials.add_trial'))

        query = "INSERT INTO trials (trial_name, start_date, end_date, status, participant_id) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (trial_name, start_date, end_date, status, participant_id))
            trial_id = cursor.lastrowid  # Get the ID of the newly inserted trial
        connection.commit()

        # Prepare data for visualization and add metadata
        prepare_visualization_data(trial_id)

        flash("New trial added successfully!", "success")
        return redirect(url_for('trials.show_trials'))

    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()

    return render_template("trials/add_trial.html", participants=participants)

# Route to edit an existing trial
@trials.route('/trials/edit/<int:trial_id>', methods=['GET', 'POST'])
def edit_trial(trial_id):
    connection = get_db()
    if request.method == 'POST':
        trial_name = request.form['trial_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']
        participant_id = request.form['participant_id']

        query = """
            UPDATE trials
            SET trial_name = %s, start_date = %s, end_date = %s, status = %s, participant_id = %s
            WHERE trial_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (trial_name, start_date, end_date, status, participant_id, trial_id))
        connection.commit()
        flash("Trial updated successfully!", "success")
        return redirect(url_for('trials.show_trials'))

    query = "SELECT * FROM trials WHERE trial_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (trial_id,))
        trial = cursor.fetchone()

    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()

    return render_template("trials/edit_trial.html", trial=trial, participants=participants)

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
