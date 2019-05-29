from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, StringField, SubmitField
from flask_bootstrap import Bootstrap
import seoonpage as SEO

# App config.
DEBUG = True
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey'
 
class NameForm(Form):
    name = TextField(u"SEO Text", render_kw={'class': 'form-control', 'rows': 5})
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = NameForm(request.form)
 
    print (form.errors)
    if request.method == 'POST':
        name=request.form['name']
        name_dict=SEO.get_top_ten(name)
 
        flash(str(name_dict))
         
    return render_template('hello.html', form=form)
