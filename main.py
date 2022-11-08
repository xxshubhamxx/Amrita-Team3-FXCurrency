from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import SelectField
from wtforms.fields.html5 import DateField
import os
import pandas as pd
import operator
import plotly.express as px
from functools import reduce
  
from flask_wtf.csrf import CSRFProtect
from wtforms.csrf.core import CSRF
from hashlib import md5

app = Flask(__name__)
# csrf = CSRFProtect(app)
# csrf.init_app(app)
app.config['SECRET_KEY'] = 'fasdjfvadug7y4bek'
# app.config['WTF_CSRF_SECRET_KEY'] = 'rgvg34u4ygbrf4uh'

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

def countList(lst1, lst2):
    return reduce(operator.add, zip(lst1, lst2))

def get_cols():
    # return get_merged_df().columns[1:]
    ans = get_merged_df().columns[1:]
    idx = tuple(range(len(ans)))
    ans = tuple(ans)
    res = countList(idx, ans)
    table = tuple(res[n:n+2] for n in range(0,len(res),2))
    # print(table)
    return table
        

class NameForm(FlaskForm):
    # class Meta:
    #     csrf = False
        # csrf_class = IPAddressCSRF
    cur1 = SelectField(u'Select Currency 1:', choices=get_cols(), render_kw={'style': 'width: 30ch; height: 5ch;'})
    cur2 = SelectField(u'Select Currency 2:', choices=get_cols(), render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt1 = DateField('DatePicker', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    dt2 = DateField('DatePicker', format='%Y-%m-%d', render_kw={'style': 'width: 30ch; height: 5ch;'})
    submit = SubmitField('Submit')
    
@app.route('/', methods=['GET', 'POST'])
def index1():
    form = NameForm()
    # form.cur1.default = 49
    # form.cur2.default = 16
    # form.process()
    data = get_files()
    df = get_merged_df()

    if form.validate_on_submit():
        
        cur1 = df.columns[int(form.cur1.data[0])+1]
        cur2 = df.columns[int(form.cur2.data[0])+1]
        dt1 = form.dt1.data
        dt2 = form.dt2.data
        if dt1>=dt2:
            return render_template('index.html', form=form, message="Please enter a valid date range")
        
        df = df[[cur1,cur2,'Date']]
        df.dropna(inplace=True)
        df['ratio'] = df[cur1]/df[cur2]
        df.drop(columns=[cur1,cur2], inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['date'] = df['Date']
        df.set_index('Date', inplace=True)     
                
        df = df[(df['date'] >= dt1) & (df['date'] <= dt2)]
        # print(df)
        fig = px.line(df, x='date', y='ratio',labels={
            'date' : f' {cur1} <br> Date',
            'ratio': f'{cur2}'
        },
            title=f'{cur1.strip()} to {cur2.strip()} from {dt1} to {dt2}'
        )
        
        fig.show(id='graph',config= {'displaylogo': False})
        # return render_template('output.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    
    return render_template('index.html', title='My Form', form=form, data=data)

if __name__ == "__main__":
    app.debug = True
    app.run(port = 5111)