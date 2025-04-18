"""
Script principal para la aplicación web SimulaGram.
Esta aplicación simula la obtención de seguidores en Instagram 
interesados en ropa para perros en Chile.
"""

import pytz
from app import app

# Configuración de zona horaria para Chile (CLT)
CHILE_TZ = pytz.timezone('America/Santiago')

@app.template_filter('chile_time')
def format_chile_time(fecha_utc, format_str='%d-%m-%Y %H:%M:%S'):
    """Filtro para formatear fechas en hora de Chile"""
    if fecha_utc:
        if fecha_utc.tzinfo is None:
            fecha_utc = pytz.UTC.localize(fecha_utc)
        fecha_chile = fecha_utc.astimezone(CHILE_TZ)
        return fecha_chile.strftime(format_str)
    return ""

# Este archivo es el punto de entrada para Gunicorn
# No se necesita más código aquí ya que todo se importa de app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)