from flask import Blueprint, render_template, request
from app.db_connect import get_db
from ..functions import generate_statistics, generate_visualizations, fetch_and_filter_data

visuals = Blueprint('visuals', __name__)

@visuals.route('/visuals', methods=['GET', 'POST'])
def show_visuals():
    connection = get_db()
    query = "SELECT trial_id, trial_name FROM trials"
    with connection.cursor() as cursor:
        cursor.execute(query)
        trials = cursor.fetchall()

    plot_html = None
    stats = None  # Initialize stats to None
    selected_trial = None
    start_date = None
    end_date = None

    if request.method == 'POST':
        # Get user inputs
        selected_trial = request.form.get('trial_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Fetch and filter data based on user inputs
        df = fetch_and_filter_data(selected_trial, start_date, end_date)

        # Generate statistics and visualizations
        if not df.empty:
            stats = generate_statistics(df)
            plot_html = generate_visualizations(df, selected_trial)
    else:
        # Fetch all data if no filter is applied
        df = fetch_and_filter_data(None, None, None)
        if not df.empty:
            stats = generate_statistics(df)
            plot_html = generate_visualizations(df, None)

    return render_template('visuals/visuals.html', trials=trials, plot_html=plot_html, stats=stats, selected_trial=selected_trial, start_date=start_date, end_date=end_date)