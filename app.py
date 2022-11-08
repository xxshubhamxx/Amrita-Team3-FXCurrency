from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import SelectField
from wtforms.fields.html5 import DateField
import os
import pandas as pd
import plotly.express as px

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
    cur1 = SelectField(u'Select Currency 1:', choices=get_merged_df().columns[1:], render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt1 = DateField('DatePicker', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt2 = DateField('DatePicker', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    submit = SubmitField('Submit')
    
@app.route('/', methods=['GET', 'POST'])
def index1():
    form = NameForm()
    data = get_files()
    df = get_merged_df()

    if form.validate_on_submit():
        
        
        cur1 = form.cur1.data
        dt1 = form.dt1.data
        dt2 = form.dt2.data
        
        if dt1>=dt2:
            return render_template('index.html', form=form, message="Please enter a valid date range")
        
        df = df[[cur1,'Date']]
        df.dropna(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['date'] = df['Date']
        df.set_index('Date', inplace=True)     
                
        df = df[(df['date'] >= dt1) & (df['date'] <= dt2)]
        # print(df)
        fig = px.line(df, x='date', y=cur1,  labels={'date' : f' {cur1} <br> Date' },
                 title=f'U.S. dollar (USD) to {cur1.strip()} from {dt1} to {dt2}')
        fig.show(id='graph',config= {'displaylogo': False}
                )
        # return render_template('output.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    
    return render_template('index.html', title='My Form', form=form, data=data)

if __name__ == "__main__":
    app.debug = True
    app.run()