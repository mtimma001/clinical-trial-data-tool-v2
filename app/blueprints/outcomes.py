from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

outcomes = Blueprint('outcomes', __name__)

# Route to display all outcomes
@outcomes.route('/outcomes')
def show_outcomes():
    connection = get_db()
    query = """
        SELECT o.outcome_id, o.participant_id, o.trial_id, o.outcome_date, o.outcome_details, o.result, 
               p.first_name, p.last_name, t.trial_name
        FROM outcomes o
        JOIN participants p ON o.participant_id = p.participant_id
        JOIN trials t ON o.trial_id = t.trial_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Convert result to Pandas DataFrame
    df = pd.DataFrame(result,
                      columns=['outcome_id', 'trial_id', 'outcome_date', 'outcome_details', 'result',
                               'first_name', 'last_name', 'trial_name'])

    # Concatenate first and last names
    df['full_name'] = df['first_name'] + ' ' + df['last_name']

    # Drop the first_name and last_name columns
    df = df.drop(columns=['first_name', 'last_name'])

    # Add action buttons for editing and deleting
    df['Actions'] = df['outcome_id'].apply(lambda o_id:
                                           f'<a href="{url_for("outcomes.edit_outcome", outcome_id=o_id)}" class="btn btn-sm btn-warning">Edit</a> '
                                           f'<form action="{url_for("outcomes.delete_outcome", outcome_id=o_id)}" method="post" style="display:inline;">'
                                           f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                           )

    # Convert DataFrame to HTML for display
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)
    table_html = table_html.split('<tbody>')[1].split('</tbody>')[0]
    return render_template("outcomes/outcomes.html", table=table_html)

# Route to add a new outcome
@outcomes.route('/outcomes/add', methods=['GET', 'POST'])
def add_outcome():
    connection = get_db()
    if request.method == 'POST':
        participant_id = request.form['participant_id']
        trial_id = request.form['trial_id']
        outcome_date = request.form['outcome_date']
        outcome_details = request.form['outcome_details']
        result = request.form['result']

        query = "INSERT INTO outcomes (participant_id, trial_id, outcome_date, outcome_details, result) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (participant_id, trial_id, outcome_date, outcome_details, result))
        connection.commit()
        flash("New outcome added successfully!", "success")
        return redirect(url_for('outcomes.show_outcomes'))

    # Fetch participants and trials for form dropdowns
    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()
        cursor.execute("SELECT trial_id, trial_name FROM trials")
        trials = cursor.fetchall()

    return render_template("outcomes/add_outcome.html", participants=participants, trials=trials)

# Route to edit an existing outcome
@outcomes.route('/outcomes/edit/<int:outcome_id>', methods=['GET', 'POST'])
def edit_outcome(outcome_id):
    connection = get_db()
    if request.method == 'POST':
        participant_id = request.form['participant_id']
        trial_id = request.form['trial_id']
        outcome_date = request.form['outcome_date']
        outcome_details = request.form['outcome_details']
        result = request.form['result']

        query = """
            UPDATE outcomes 
            SET participant_id = %s, trial_id = %s, outcome_date = %s, outcome_details = %s, result = %s 
            WHERE outcome_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (participant_id, trial_id, outcome_date, outcome_details, result, outcome_id))
        connection.commit()
        flash("Outcome data updated successfully!", "success")
        return redirect(url_for('outcomes.show_outcomes'))

    # Fetch outcome data for editing
    query = "SELECT * FROM outcomes WHERE outcome_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (outcome_id,))
        outcome = cursor.fetchone()

    # Fetch participants and trials for dropdowns
    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()
        cursor.execute("SELECT trial_id, trial_name FROM trials")
        trials = cursor.fetchall()

    return render_template("outcomes/edit_outcome.html", outcome=outcome, participants=participants, trials=trials)

# Route to delete an outcome
@outcomes.route('/outcomes/delete/<int:outcome_id>', methods=['POST'])
def delete_outcome(outcome_id):
    connection = get_db()
    query = "DELETE FROM outcomes WHERE outcome_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (outcome_id,))
    connection.commit()
    flash("Outcome deleted successfully!", "success")
    return redirect(url_for('outcomes.show_outcomes'))
