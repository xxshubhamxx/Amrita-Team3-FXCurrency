from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import SubmitField
from wtforms import SelectField
from wtforms.fields.html5 import DateField
import os
import pandas as pd
import calendar
import plotly.express as px

# from django.utils.html import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
Bootstrap(app)

def get_files():
    files = []
    for file in os.listdir(os.path.join(os.getcwd(),"Currency_Conversion_Test_Data")):
        files.append(file)
    return files

def get_merged_df():
    data = get_files()
    df = pd.read_csv(os.path.join(os.getcwd(),"Currency_Conversion_Test_Data",data[0]))
    data.pop(0)
    for file in data:
        filepath = os.path.join(os.getcwd(),"Currency_Conversion_Test_Data",file)
        df = pd.concat([df, pd.read_csv(filepath)])
    return df

class NameForm(FlaskForm):
    currency = SelectField(u'Select Currency:', choices=get_merged_df().columns[1:], render_kw={'style': 'width: 30ch; height: 5ch;'})
    start_date = DateField('Enter Start Date', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    end_date = DateField('Enter End Date', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    interval = SelectField(u'Select Interval:', choices=['daily','monthly','yearly'], render_kw={'style': 'width: 30ch; height: 5ch;'})
    submit = SubmitField('Submit')

def get_cur_str(currency_string):
    currency_string = str(currency_string)
    return currency_string[0:-7]

def get_cur_code(currency_string):
    currency_string = str(currency_string)
    return currency_string[-4:-1]
 
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    df = get_merged_df()

    if form.validate_on_submit():
        
        currency = form.currency.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        interval = form.interval.data
        currency_name = get_cur_str(currency.strip())
        currency_code = get_cur_code(currency.strip())
        if start_date>=end_date:
            return render_template('index.html', form=form, message="Please enter a valid date range")
        
        df = df[[currency,'Date']]
        df.dropna(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['date'] = df['Date']
        df.set_index('Date', inplace=True)   
         
        df['year'] = pd.DatetimeIndex(df['date']).year 
        df['month'] = pd.DatetimeIndex(df['date']).month
        df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])
        df['month'] = df['year'].astype(str) +", "+ df['month'].astype(str)
        
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        title_str = f'U.S. dollar (USD) to {currency_name} ({currency_code}) from {start_date} to {end_date}'

        if interval == 'daily':
            fig = px.line(df, x='date', y=currency,  labels={'date' : f'Date', currency: f'{currency_name} ({currency_code})' },
                title=title_str)
            
        elif interval == 'monthly':
            month_df=df.groupby(['month','year'], as_index=False)[currency].mean()
            def make_date(months):
                a = []
                for month in months:
                    month = str(month)
                    mn = month[-3:]
                    yr = month[0:4]
                    mn = datetime.strptime(mn, '%b').month
                    ans = f'01-{mn}-{yr}'
                    a.append(datetime.strptime(ans, '%d-%m-%Y').date())
                return a
            month_df['date'] = make_date(month_df['month'])
            month_df = month_df[(month_df['date'] >= start_date) & (month_df['date'] <= end_date)]
            fig = px.line(month_df, x='month', y=currency,  labels={'month' : f'Month' , currency: f'{currency_name} ({currency_code})' },
                title=title_str)
            
        elif interval == 'yearly':
            year_df=df.groupby('year', as_index=False)[currency].mean()
            def make_date(year):
                a = []
                for yr in year:
                    ans = f'01-06-{yr}'
                    a.append(datetime.strptime(ans, '%d-%m-%Y').date())
                return a
            year_df['date'] = make_date(year_df['year'])
            year_df = year_df[(year_df['date'] >= start_date) & (year_df['date'] <= end_date)]
            fig = px.line(year_df, x='year', y=currency,  labels={'year' : f'Year' , currency: f'{currency_name} ({currency_code})' },
                title=title_str)
            fig.update_traces(mode="markers+lines")
        else:
            return render_template('index.html', form=form, message="Please enter a valid interval")
        
        fig.update_traces(hovertemplate =
            '1 USD = <b> %{y:.2f} </b>'+ f'{currency_code}'+
            '<br>in: %{x}<br>')
        # To add custom text to every hover label, add this to the hovertemplate:
            # '<b>%{text}</b>',
            # text = [c_code for i in range(len(fig.data[0].x))]
            
        fig.update_xaxes(showspikes=True)
        fig.update_yaxes(showspikes=True)
        fig.write_html('templates/plot.html',config= {'displaylogo': False})
        return render_template('plot.html')
        # plot_html = escape(render_template('plot.html'))
        # return render_template('index.html', plot=plot_html, form=form)
    
    return render_template('index.html', title='My Form', form=form)

if __name__ == "__main__":
    app.debug = True
    app.run()