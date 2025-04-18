"""
Script principal para la aplicación web SimulaGram.
Esta aplicación simula la obtención de seguidores en Instagram 
interesados en ropa para perros en Chile.
"""

from app import app

# Este archivo es el punto de entrada para Gunicorn
# No se necesita más código aquí ya que todo se importa de app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)