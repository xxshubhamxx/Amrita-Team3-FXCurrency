from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
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
    cur1 = SelectField(u'Select Currency:', choices=get_merged_df().columns[1:], render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt1 = DateField('Enter Start Date', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt2 = DateField('Enter End Date', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    interval = SelectField(u'Select Interval:', choices=['daily','monthly','yearly'], render_kw={'style': 'width: 30ch; height: 5ch;'})
    submit = SubmitField('Submit')

def get_cur_str(val):
    val = str(val)
    return val[1:-5]

def get_cur_code(val):
    val = str(val)
    return val[-4:-1]
 
@app.route('/', methods=['GET', 'POST'])
def index1():
    form = NameForm()
    df = get_merged_df()

    if form.validate_on_submit():
        
        cur1 = form.cur1.data
        dt1 = form.dt1.data
        dt2 = form.dt2.data
        interval = form.interval.data
        
        if dt1>=dt2:
            return render_template('index.html', form=form, message="Please enter a valid date range")
        
        df = df[[cur1,'Date']]
        df.dropna(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['date'] = df['Date']
        df.set_index('Date', inplace=True)   
         
        df['year'] = pd.DatetimeIndex(df['date']).year 
        df['month'] = pd.DatetimeIndex(df['date']).month
        df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])
        df['month'] = df['year'].astype(str) +", "+ df['month'].astype(str)
         
        year_df=df.groupby('year', as_index=False)[cur1].mean()
        month_df=df.groupby('month', as_index=False)[cur1].mean()
        
        df = df[(df['date'] >= dt1) & (df['date'] <= dt2)]
        
        c_code = get_cur_code(f'{cur1.strip()}')

        if interval == 'daily':
            fig = px.line(df, x='date', y=cur1,  labels={'date' : f'Date' },
                 title=f'U.S. dollar (USD) to {cur1.strip()} from {dt1} to {dt2}')
        elif interval == 'monthly':
            fig = px.line(month_df, x='month', y=cur1,  labels={'month' : f'Month' },
                 title=f'U.S. dollar (USD) to {cur1.strip()} from {dt1} to {dt2}')
        elif interval == 'yearly':
            fig = px.line(year_df, x='year', y=cur1,  labels={'year' : f'Year' },
                 title=f'U.S. dollar (USD) to {cur1.strip()} from {dt1} to {dt2}')
            fig.update_traces(mode="markers+lines")
        else:
            return render_template('index.html', form=form, message="Please enter a valid interval")
        
        fig.update_traces(hovertemplate =
            '1 USD = <b> %{y:.2f} </b>'+ f'{c_code}'+
            '<br>in: %{x}<br>')
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