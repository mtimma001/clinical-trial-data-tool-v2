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
    df = pd.DataFrame(result, columns=['outcome_id', 'participant_id', 'trial_id', 'outcome_date', 'outcome_details', 'result', 'first_name', 'last_name', 'trial_name'])

    # Add full name column
    df['full_name'] = df['first_name'] + ' ' + df['last_name']

    # Drop unnecessary columns
    df = df.drop(columns=['first_name', 'last_name'])

    # Convert the DataFrame to a list of dictionaries for rendering in the template
    outcomes = df.to_dict('records')

    # Fetch participants and trials for dropdowns
    with connection.cursor() as cursor:
        cursor.execute("SELECT participant_id, first_name, last_name FROM participants")
        participants = cursor.fetchall()
        cursor.execute("SELECT trial_id, trial_name FROM trials")
        trials = cursor.fetchall()

    return render_template("outcomes.html", outcomes=outcomes, participants=participants, trials=trials)

# Route to add a new outcome
@outcomes.route('/outcomes/add', methods=['POST'])
def add_outcome():
    participant_id = request.form['participant_id']
    trial_id = request.form['trial_id']
    outcome_date = request.form['outcome_date']
    outcome_details = request.form['outcome_details']
    result = request.form['result']

    connection = get_db()
    query = "INSERT INTO outcomes (participant_id, trial_id, outcome_date, outcome_details, result) VALUES (%s, %s, %s, %s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(query, (participant_id, trial_id, outcome_date, outcome_details, result))
    connection.commit()

    flash("Outcome added successfully!", "success")
    return redirect(url_for('outcomes.show_outcomes'))

# Route to edit an existing outcome
@outcomes.route('/outcomes/edit/<int:outcome_id>', methods=['POST'])
def edit_outcome(outcome_id):
    participant_id = request.form['participant_id']
    trial_id = request.form['trial_id']
    outcome_date = request.form['outcome_date']
    outcome_details = request.form['outcome_details']
    result = request.form['result']

    connection = get_db()
    query = """
        UPDATE outcomes
        SET participant_id = %s, trial_id = %s, outcome_date = %s, outcome_details = %s, result = %s
        WHERE outcome_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (participant_id, trial_id, outcome_date, outcome_details, result, outcome_id))
    connection.commit()
    flash("Outcome updated successfully!", "success")
    return redirect(url_for('outcomes.show_outcomes'))

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
