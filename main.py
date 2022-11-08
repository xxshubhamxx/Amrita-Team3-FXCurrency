from flask import Flask
from flask import render_template
from flask import redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
import os
import pandas as pd

import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
Bootstrap(app)

def get_files():
    files = []
    for file in os.listdir(os.path.join(os.getcwd(),"Currency_Conversion_Test_Data")):
        files.append(file)
    return files

def get_choices():
    data = get_files()
    df = pd.read_csv(os.path.join(os.getcwd(),"Currency_Conversion_Test_Data",data[0]))
    data.pop(0)
    for file in data:
        filepath = os.path.join(os.getcwd(),"Currency_Conversion_Test_Data",file)
        df = pd.concat([df, pd.read_csv(filepath)])
    return df

class NameForm(FlaskForm):
    cur1 = SelectMultipleField(u'Select Currency 1:', choices=get_choices().columns[1:], render_kw={'style': 'width: 10ch; height: 30ch;'})
    cur2 = SelectMultipleField(u'Select Currency 2:', choices=get_choices().columns[1:], render_kw={'style': 'width: 10ch; height: 30ch;'} )
    submit = SubmitField('Submit')
    
@app.route('/', methods=['GET', 'POST'])
def index1():
    form = NameForm()
    data = get_files()
    df = get_choices()

    if form.validate_on_submit():
        
        
        cur1 = form.cur1.data[0]
        cur2 = form.cur2.data[0]
        df = df[[cur1,cur2,'Date']]
        df.dropna(inplace=True)
        df.set_index('Date', inplace=True)
        print(df)
        
        def create_figure():
            fig = Figure()
            axis = fig.add_subplot(1, 1, 1)
            xs = df.iloc[:,0].values
            ys = df.iloc[:,1].values
            axis.plot(xs, ys)
            return fig
        
        
        fig = create_figure()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        # return Response(output.getvalue(), mimetype='image/png')
    
    
        
        return render_template('output.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
    
    return render_template('index.html', title='My Form', form=form, data=data)


if __name__ == "__main__":
    app.debug = True
    app.run()