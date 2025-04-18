from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Simulacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    objetivo_seguidores = db.Column(db.Integer, default=100)
    seguidores_alcanzados = db.Column(db.Integer, default=0)
    regiones_objetivo = db.Column(db.Text, nullable=True)  # Almacenado como JSON
    edades_objetivo = db.Column(db.Text, nullable=True)    # Almacenado como JSON
    sexos_objetivo = db.Column(db.Text, nullable=True)     # Almacenado como JSON
    completada = db.Column(db.Boolean, default=False)
    
    # Relación con seguidores
    seguidores = db.relationship('Seguidor', backref='simulacion', lazy=True)
    # Relación con publicaciones
    publicaciones = db.relationship('Publicacion', backref='simulacion', lazy=True)
    # Relación con estadísticas
    estadisticas = db.relationship('Estadistica', backref='simulacion', lazy=True)

class Seguidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    simulacion_id = db.Column(db.Integer, db.ForeignKey('simulacion.id'), nullable=False)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    sexo = db.Column(db.String(20), nullable=False)
    edad = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Publicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    simulacion_id = db.Column(db.Integer, db.ForeignKey('simulacion.id'), nullable=False)
    sexo_objetivo = db.Column(db.String(20), nullable=False)
    edad_objetivo = db.Column(db.String(20), nullable=False)
    region_objetivo = db.Column(db.String(50), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    vistos = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Estadistica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    simulacion_id = db.Column(db.Integer, db.ForeignKey('simulacion.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    seguidores_total = db.Column(db.Integer, default=0)
    seguidores_hoy = db.Column(db.Integer, default=0)
    publicaciones_total = db.Column(db.Integer, default=0)
    publicaciones_hoy = db.Column(db.Integer, default=0)
    
    # Estadísticas demográficas (almacenadas como JSON)
    distribucion_sexo = db.Column(db.Text, nullable=True)  
    distribucion_edad = db.Column(db.Text, nullable=True)  
    distribucion_region = db.Column(db.Text, nullable=True)