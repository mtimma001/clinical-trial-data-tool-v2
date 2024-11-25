import pandas as pd
import plotly.express as px
import plotly.io as pio
from app.db_connect import get_db
from datetime import datetime

def generate_statistics(df):
    stats = {
        'total_outcomes': df['outcome_id'].nunique(),
        'total_participants': df['participant_id'].nunique(),
        'total_trials': df['trial_id'].nunique()
    }
    return stats


def plot_outcomes_by_trial(df, selected_trial):
    if selected_trial:
        df = df[df['trial_id'] == int(selected_trial)]

    # Count the number of outcomes for each trial
    trial_counts = df['trial_name'].value_counts().reset_index()
    trial_counts.columns = ['trial_name', 'count']

    # Create the bar chart
    fig = px.bar(trial_counts, x='trial_name', y='count', title='Number of Outcomes by Trial',
                 labels={'trial_name': 'Trial Name', 'count': 'Number of Outcomes'},
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      title={'x': 0.5, 'xanchor': 'center'})
    return pio.to_html(fig, full_html=False)

def plot_outcomes_over_time(df):
    df['outcome_date'] = pd.to_datetime(df['outcome_date'])
    df.set_index('outcome_date', inplace=True)
    df = df.resample('ME').size().reset_index(name='count')
    fig = px.line(df, x='outcome_date', y='count', title='Outcomes Over Time',
                  labels={'outcome_date': 'Outcome Date', 'count': 'Number of Outcomes'},
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      title={'x': 0.5, 'xanchor': 'center'})
    return pio.to_html(fig, full_html=False)

def custom_visualization(df, x_col, y_col, kind='bar'):
    fig = None
    if kind == 'bar':
        fig = px.bar(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}',
                     labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
    elif kind == 'line':
        fig = px.line(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}',
                      labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()},
                      color_discrete_sequence=px.colors.qualitative.Plotly)
    elif kind == 'scatter':
        fig = px.scatter(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}',
                         labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()},
                         color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      title={'x': 0.5, 'xanchor': 'center'})
    return pio.to_html(fig, full_html=False)

def fetch_and_filter_data(selected_trial, start_date, end_date):
    connection = get_db()
    if not start_date:
        start_date = '1900-01-01'  # Use a very early date if not provided
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')  # Use today's date if not provided

    data_query = """
        SELECT o.outcome_id, o.outcome_date, o.result, t.trial_name, t.trial_id, p.first_name, p.last_name, p.participant_id
        FROM outcomes o
        JOIN trials t ON o.trial_id = t.trial_id
        JOIN participants p ON o.participant_id = p.participant_id
        WHERE (%s IS NULL OR %s = '' OR o.trial_id = %s)
          AND o.outcome_date >= %s
          AND o.outcome_date <= %s
    """
    with connection.cursor() as cursor:
        cursor.execute(data_query, (selected_trial, selected_trial, selected_trial, start_date, end_date))
        result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['outcome_id', 'outcome_date', 'result', 'trial_name', 'trial_id', 'first_name', 'last_name', 'participant_id'])
    return df

def generate_visualizations(df, selected_trial):
    if selected_trial:
        trial_name = df['trial_name'].iloc[0]
    else:
        trial_name = "All Trials"

    heading_html = f"<h3 class='text-center'>{trial_name}</h3>"

    visualizations = [plot_outcomes_by_trial(df, selected_trial), plot_outcomes_over_time(df)]

    # Histogram for results
    fig = px.histogram(df, x='result', title='Distribution of Results',
                       labels={'result': 'Result'},
                       color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      title={'x': 0.5, 'xanchor': 'center'})
    visualizations.append(pio.to_html(fig, full_html=False))

    return heading_html + ''.join(visualizations)