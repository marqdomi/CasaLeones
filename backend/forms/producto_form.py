from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    precio_unitario = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    categoria = StringField('Categoría', validators=[DataRequired(), Length(max=50)])
    estacion = SelectField(
        'Estación',
        choices=[('taqueros','Taqueros'), ('comal','Comal'), ('bebidas','Bebidas')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Guardar')