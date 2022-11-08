from flask import Flask
from flask import render_template
from flask import redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
import os
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
Bootstrap(app)

def get_files():
    files = []
    for file in os.listdir(os.path.join(os.getcwd(),"Currency_Conversion_Test_Data")):
        file = file[21:25]
        files.append(file)
    return files

class NameForm(FlaskForm):
    yno = SelectMultipleField(u'Select Year Number:', choices=get_files(), render_kw={'style': 'width: 10ch; height: 30ch;'} )
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():

        yno = form.yno.data[0]
        
        filepath = os.path.join(os.getcwd(),"Currency_Conversion_Test_Data","Exchange_Rate_Report_")
        filepath += yno+".csv"
        df = pd.read_csv(filepath)
        
        print(df.head())
        
        return redirect(url_for('output', yno=yno))
    data = get_files()
    return render_template('index.html', title='My Form', form=form, data=data)

@app.route('/output')
def output():
    yno = request.args.get('yno')
    return render_template('output.html', yno = yno)

if __name__ == "__main__":
    app.debug = True
    app.run()