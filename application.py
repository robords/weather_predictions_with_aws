from weather_predictions import (get_forecast_data, plot_forecast_data, get_list_of_services,
                                 get_list_of_states, get_homepage_locations_list)
import matplotlib

matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import pyplot as plt
from flask import Flask, jsonify, Response, render_template, request
import os
import io
import pandas as pd
import seaborn as sns

plt.rcParams["figure.autolayout"] = True


def plot_service(service, type, percentile):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax = sns.set(style="darkgrid")
    if service == 'all':
        if type == 'cost':
            timestamp, p10, p50, p90 = plot_forecast_data('all', "Cost_Forecastv3", 'all')
            df = pd.DataFrame(list(zip(timestamp, p10, p50, p90)), columns=['date', 'p10', 'p50', 'p90'])
            df['date'] = pd.to_datetime(df['date'])
            chart = sns.lineplot(x='date', y='value', hue='variable', data=pd.melt(df, ['date']))
        else:
            timestamp, p10, p50, p90 = plot_forecast_data('all', "Snow_Forecast", 'all')
            df = pd.DataFrame(list(zip(timestamp, p10, p50, p90)), columns=['date', 'p10', 'p50', 'p90'])
            df['date'] = pd.to_datetime(df['date'])
            chart = sns.lineplot(x='date', y='value', hue='variable', data=pd.melt(df, ['date']))
    else:
        if percentile == 'all':
            if type == 'cost':
                timestamp, p10, p50, p90 = plot_forecast_data(f'{service}', "Cost_Forecastv3", 'all')
                df = pd.DataFrame(list(zip(timestamp, p10, p50, p90)), columns=['date', 'p10', 'p50', 'p90'])
                df['date'] = pd.to_datetime(df['date'])
                chart = sns.lineplot(x='date', y='value', hue='variable', data=pd.melt(df, ['date']))
            else:
                timestamp, p10, p50, p90 = plot_forecast_data(f'{service}', "Snow_Forecast", 'all')
                df = pd.DataFrame(list(zip(timestamp, p10, p50, p90)), columns=['date', 'p10', 'p50', 'p90'])
                df['date'] = pd.to_datetime(df['date'])
                chart = sns.lineplot(x='date', y='value', hue='variable', data=pd.melt(df, ['date']))
        else:
            if type == 'cost':
                xs, ys = plot_forecast_data(f'{service}', "Cost_Forecastv3", percentile)
                df = pd.DataFrame(list(zip(xs, ys)), columns=['date', 'cost'])
                df['date'] = pd.to_datetime(df['date'])
                chart = sns.lineplot(x='date', y='cost', data=df)
            else:
                xs, ys = plot_forecast_data(f'{service}', "Snow_Forecast", percentile)
                df = pd.DataFrame(list(zip(xs, ys)), columns=['date', 'precipitation'])
                df['date'] = pd.to_datetime(df['date'])
                chart = sns.lineplot(x='date', y='precipitation', data=df)
    for item in chart.get_xticklabels():
        item.set_rotation(45)
    chart.set(title=f'{service} Forecast')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def index():
    try:
        endpoint = os.environ['API_ENDPOINT']
    except KeyError:
        endpoint = 'Local'
    df = get_homepage_locations_list()
    errors = []
    results = {}
    img = "/states/VT/all"
    if request.method == "POST":
        try:
            subset_id = request.form['location_filter']
            df_filtered = df.loc[df["Locations"].str.contains(subset_id)]
            if len(subset_id) == 2:
                img = f"/states/{subset_id}/all"
            else:
                img = "/static/scoliid_an_open_MacBook_on_an_outdoor_patio_table_starting_to_g_1b98227d-fc02-42f6-bcef-87122aed48e7.png"
        except:
            errors.append(
                f"{request.form['location_filter']} isn't a location, please try again."
            )
    else:
        df_filtered = df
        img = "/static/scoliid_an_open_MacBook_on_an_outdoor_patio_table_starting_to_g_1b98227d-fc02-42f6-bcef-87122aed48e7.png"

    return render_template('index.html', environment=endpoint, errors=errors, results=results,
                           tables=[df_filtered.to_html(
                               classes='data table table-striped table-bordered table-hover table-sm',
                               index=False, escape=False, header=True)],
                           service=img  # , mycolours=mycolours
                           )


@application.route('/about', methods=['GET'])
def about():
    try:
        endpoint = os.environ['API_ENDPOINT']
    except KeyError:
        endpoint = 'Local'
    return render_template('report.html', environment=endpoint)

@application.route('/aboutme', methods=['GET'])
def about_me():
    try:
        endpoint = os.environ['API_ENDPOINT']
    except KeyError:
        endpoint = 'Local'
    return render_template('about_me.html', environment=endpoint)


@application.route('/costs', methods=['GET'])
def costs():
    try:
        endpoint = os.environ['API_ENDPOINT']
    except KeyError:
        endpoint = 'Local'
    df = get_list_of_services()
    return render_template('tables.html', tables=[df.to_html(
        classes='data table table-striped table-bordered table-hover table-sm',
        index=False, escape=False, header=True)],
                           environment=endpoint, page_type='Costs')


@application.route('/states', methods=['GET'])
def states():
    try:
        endpoint = os.environ['API_ENDPOINT']
    except KeyError:
        endpoint = 'Local'
    df = get_list_of_states()
    return render_template('tables.html', tables=[df.to_html(
        classes='data table table-striped table-bordered table-hover table-sm',
        index=False, escape=False)],
                           environment=endpoint, page_type='States')


@application.route('/states/<some_state>')
def weather_page(some_state):
    data = get_forecast_data(f'{some_state}', "Snow_Forecast", '')
    resp = jsonify(data)
    resp.status_code = 200
    return resp


@application.route('/states/<some_state>/all')
def plot_weather_all(some_state):
    return plot_service(some_state, 'weather', 'all')

@application.route('/states/<some_state>/p10')
def plot_weather_p10(some_state):
    return plot_service(some_state, 'weather', 'p10')

@application.route('/states/<some_state>/p50')
def plot_weather_p50(some_state):
    return plot_service(some_state, 'weather', 'p50')

@application.route('/states/<some_state>/p90')
def plot_weather_p90(some_state):
    return plot_service(some_state, 'weather', 'p90')


@application.route('/costs/<service>')
def cost_page(service):
    data = get_forecast_data(f'{service}', "Cost_Forecastv3", '')
    resp = jsonify(data)
    resp.status_code = 200
    return resp

@application.route('/costs/<service>/all')
def plot_service_all(service):
    return plot_service(service, 'cost', 'all')

@application.route('/costs/<service>/p50')
def plot_service_p50(service):
    return plot_service(service, 'cost', 'p50')


@application.route('/costs/<service>/p10')
def plot_service_p10(service):
    return plot_service(service, 'cost', 'p10')


@application.route('/costs/<service>/p90')
def plot_service_p90(service):
    return plot_service(service, 'cost', 'p90')


if __name__ == '__main__':
    application.run(host='127.0.0.1', port=8080, debug=True)
