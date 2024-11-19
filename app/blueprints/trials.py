from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

trials = Blueprint('trials', __name__)

# Route to display all trials
@trials.route('/trials')
def show_trials():
    connection = get_db()
    query = "SELECT * FROM trials"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert result to Pandas DataFrame
    df = pd.DataFrame(result, columns=['trial_id', 'trial_name', 'start_date', 'end_date', 'status'])

    # Add action buttons for editing and deleting
    df['Actions'] = df['trial_id'].apply(lambda t_id:
                                         f'<a href="{url_for("trials.edit_trial", trial_id=t_id)}" class="btn btn-sm btn-info">Edit</a> '
                                         f'<form action="{url_for("trials.delete_trial", trial_id=t_id)}" method="post" style="display:inline;">'
                                         f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                         )

    # Convert DataFrame to HTML for display
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)
    return render_template("trials/trials.html", table=table_html)

# Route to add a new trial
@trials.route('/trials/add', methods=['GET', 'POST'])
def add_trial():
    if request.method == 'POST':
        trial_name = request.form['trial_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        connection = get_db()
        query = "INSERT INTO trials (trial_name, start_date, end_date, status) VALUES (%s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (trial_name, start_date, end_date, status))
        connection.commit()
        flash("New trial added successfully!", "success")
        return redirect(url_for('trials.show_trials'))

    return render_template("trials/add_trial.html")

# Route to edit an existing trial
@trials.route('/trials/edit/<int:trial_id>', methods=['GET', 'POST'])
def edit_trial(trial_id):
    connection = get_db()
    if request.method == 'POST':
        trial_name = request.form['trial_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

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

    # Fetch trial data for editing
    query = "SELECT * FROM trials WHERE trial_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (trial_id,))
        trial = cursor.fetchone()

    return render_template("trials/edit_trial.html", trial=trial)

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
