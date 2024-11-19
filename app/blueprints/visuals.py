from flask import Blueprint, render_template, request
from app.db_connect import get_db
import pandas as pd
import plotly.express as px

visuals = Blueprint('visuals', __name__)

@visuals.route('/visuals', methods=['GET', 'POST'])
def show_visuals():
    connection = get_db()
    query = "SELECT trial_id, trial_name FROM trials"
    with connection.cursor() as cursor:
        cursor.execute(query)
        trials = cursor.fetchall()

    # Initialize parameters
    selected_trial = None
    start_date = None
    end_date = None
    plot_html = None

    if request.method == 'POST':
        # Get user inputs
        selected_trial = request.form.get('trial_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Fetch and filter data based on user inputs
        data_query = """
            SELECT o.outcome_date, o.result, t.trial_name, p.first_name, p.last_name
            FROM outcomes o
            JOIN trials t ON o.trial_id = t.trial_id
            JOIN participants p ON o.participant_id = p.participant_id
            WHERE (%s IS NULL OR o.trial_id = %s)
              AND (%s IS NULL OR o.outcome_date >= %s)
              AND (%s IS NULL OR o.outcome_date <= %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(data_query, (selected_trial, selected_trial, start_date, start_date, end_date, end_date))
            result = cursor.fetchall()

        # Create a DataFrame from the filtered data
        df = pd.DataFrame(result, columns=['outcome_date', 'result', 'trial_name', 'first_name', 'last_name'])

        # Example visualization: Line chart for outcomes over time
        if not df.empty:
            df['outcome_date'] = pd.to_datetime(df['outcome_date'])
            outcome_trend = df.groupby('outcome_date').size().reset_index(name='Outcome Count')
            fig = px.line(outcome_trend, x='outcome_date', y='Outcome Count', title='Outcome Trends Over Time')
            plot_html = fig.to_html(full_html=False)

    return render_template('visuals/visuals.html', trials=trials, plot_html=plot_html)
