from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class URLForm(FlaskForm):
    """ 
    Main form where the user submits his form.

    https://hackersandslackers.com/flask-wtforms-forms/
    https://pythonspot.com/flask-web-forms/
    """
    # url = StringField('', [URL(message=('Not a valid url address')), DataRequired()], render_kw={"placeholder": "Enter URL Here!"})
    # TODO: URL validation.
    url = StringField('', [DataRequired()], render_kw={"placeholder": "Enter URL Here!"})
    submit = SubmitField('Bust it!')