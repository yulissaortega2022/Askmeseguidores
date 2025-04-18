import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import threading
import time
import datetime
import random
import pytz

# Configuración de zona horaria para Chile (CLT)
CHILE_TZ = pytz.timezone('America/Santiago')

def to_chile_time(fecha_utc):
    """Convierte una fecha UTC a la zona horaria de Chile"""
    if fecha_utc.tzinfo is None:
        fecha_utc = pytz.UTC.localize(fecha_utc)
    return fecha_utc.astimezone(CHILE_TZ)

def format_chile_time(fecha_utc, format_str='%d-%m-%Y %H:%M:%S'):
    """Formatea una fecha UTC a string en hora de Chile"""
    if fecha_utc:
        fecha_chile = to_chile_time(fecha_utc)
        return fecha_chile.strftime(format_str)
    return ""

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la base de datos con opciones de conexión mejoradas
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 60,  # Reciclar conexiones después de 60 segundos
    'pool_pre_ping': True,  # Verificar conexión antes de usarla
    'pool_timeout': 30,  # Tiempo de espera para obtener una conexión
    'pool_size': 5,  # Máximo de conexiones en el pool
    'max_overflow': 10  # Conexiones adicionales si es necesario
}
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'clave_secreta_desarrollo')

# Importar la base de datos y modelos
from models import db, Simulacion, Seguidor, Publicacion, Estadistica

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Importar funciones del simulador
from simulador import (
    OPENAI_API_KEY, 
    EDADES, SEXOS, REGIONES,
    generar_nombre_usuario, generar_comentario, generar_texto_publicacion,
    configurar_openai, conectar_con_ia
)

# Variables globales para la simulación
simulation_active = False
simulation_thread = None
simulation_lock = threading.Lock()
current_simulation_id = None

@app.route('/')
def index():
    """Página principal del simulador."""
    # Obtener las últimas simulaciones
    simulaciones = Simulacion.query.order_by(Simulacion.fecha_inicio.desc()).limit(5).all()
    return render_template('index.html', simulaciones=simulaciones)

@app.route('/dashboard')
def dashboard():
    """Panel de control principal con estadísticas."""
    # Obtener todas las simulaciones
    simulaciones = Simulacion.query.order_by(Simulacion.fecha_inicio.desc()).all()
    return render_template('dashboard.html', simulaciones=simulaciones)

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    """Página para configurar una nueva simulación."""
    if request.method == 'POST':
        # Obtener datos del formulario
        objetivo_seguidores = int(request.form.get('objetivo_seguidores', 100))
        regiones = request.form.getlist('regiones')
        edades = request.form.getlist('edades')
        sexos = request.form.getlist('sexos')
        
        # Crear nueva simulación
        nueva_simulacion = Simulacion(
            objetivo_seguidores=objetivo_seguidores,
            regiones_objetivo=json.dumps(regiones) if regiones else None,
            edades_objetivo=json.dumps(edades) if edades else None,
            sexos_objetivo=json.dumps(sexos) if sexos else None
        )
        
        db.session.add(nueva_simulacion)
        db.session.commit()
        
        # Guardar ID de la simulación en sesión
        session['simulacion_id'] = nueva_simulacion.id
        
        return redirect(url_for('simulacion', id=nueva_simulacion.id))
    
    return render_template('configuracion.html', regiones=REGIONES, edades=EDADES, sexos=SEXOS)

@app.route('/simulacion/<int:id>')
def simulacion(id):
    """Página para ver detalles de una simulación específica."""
    simulacion = Simulacion.query.get_or_404(id)
    
    # Obtener estadísticas de la simulación
    estadisticas = Estadistica.query.filter_by(simulacion_id=id).order_by(Estadistica.fecha.desc()).first()
    
    # Obtener los últimos 10 seguidores
    seguidores = Seguidor.query.filter_by(simulacion_id=id).order_by(Seguidor.fecha_creacion.desc()).limit(10).all()
    
    # Obtener las últimas 5 publicaciones
    publicaciones = Publicacion.query.filter_by(simulacion_id=id).order_by(Publicacion.fecha_creacion.desc()).limit(5).all()
    
    return render_template(
        'simulacion.html', 
        simulacion=simulacion, 
        estadisticas=estadisticas,
        seguidores=seguidores,
        publicaciones=publicaciones,
        simulation_active=simulation_active and current_simulation_id == id
    )

@app.route('/analisis/<int:id>')
def analisis(id):
    """Página para ver análisis detallado de una simulación."""
    simulacion = Simulacion.query.get_or_404(id)
    
    # Obtener todas las estadísticas para gráficos de evolución
    estadisticas = Estadistica.query.filter_by(simulacion_id=id).order_by(Estadistica.fecha.asc()).all()
    
    # Obtener datos demográficos para gráficos
    seguidores = Seguidor.query.filter_by(simulacion_id=id).all()
    
    # Calcular distribuciones
    dist_sexo = {}
    dist_edad = {}
    dist_region = {}
    
    for seguidor in seguidores:
        dist_sexo[seguidor.sexo] = dist_sexo.get(seguidor.sexo, 0) + 1
        dist_edad[seguidor.edad] = dist_edad.get(seguidor.edad, 0) + 1
        dist_region[seguidor.region] = dist_region.get(seguidor.region, 0) + 1
    
    return render_template(
        'analisis.html', 
        simulacion=simulacion, 
        estadisticas=estadisticas,
        dist_sexo=dist_sexo,
        dist_edad=dist_edad,
        dist_region=dist_region
    )

@app.route('/iniciar_simulacion/<int:id>')
def iniciar_simulacion(id):
    """Inicia una simulación."""
    global simulation_active, simulation_thread, current_simulation_id
    
    # Si ya hay una simulación en curso, detenla
    if simulation_active:
        return jsonify(success=False, message="Ya hay una simulación en curso.")
    
    # Obtener la simulación
    simulacion = Simulacion.query.get_or_404(id)
    if simulacion.completada:
        return jsonify(success=False, message="Esta simulación ya fue completada.")
    
    # Actualizar variables globales
    simulation_active = True
    current_simulation_id = id
    
    # Iniciar la simulación en un hilo separado
    simulation_thread = threading.Thread(target=ejecutar_simulacion, args=(id,))
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return jsonify(success=True)

@app.route('/detener_simulacion/<int:id>')
def detener_simulacion(id):
    """Detiene una simulación en curso."""
    global simulation_active
    
    if not simulation_active or current_simulation_id != id:
        return jsonify(success=False, message="No hay simulación activa para detener.")
    
    # Marcar la simulación como inactiva
    simulation_active = False
    
    return jsonify(success=True)

@app.route('/estado_simulacion/<int:id>')
def estado_simulacion(id):
    """Devuelve el estado actual de una simulación."""
    simulacion = Simulacion.query.get_or_404(id)
    
    # Obtener los últimos 20 seguidores
    seguidores = Seguidor.query.filter_by(simulacion_id=id).order_by(Seguidor.fecha_creacion.desc()).limit(20).all()
    
    # Obtener las últimas 5 publicaciones
    publicaciones = Publicacion.query.filter_by(simulacion_id=id).order_by(Publicacion.fecha_creacion.desc()).limit(5).all()
    
    # Obtener estadísticas actuales
    estadisticas = Estadistica.query.filter_by(simulacion_id=id).order_by(Estadistica.fecha.desc()).first()
    
    return jsonify({
        'id': simulacion.id,
        'activa': simulation_active and current_simulation_id == id,
        'objetivo': simulacion.objetivo_seguidores,
        'actual': simulacion.seguidores_alcanzados,
        'progreso': (simulacion.seguidores_alcanzados / simulacion.objetivo_seguidores) * 100 if simulacion.objetivo_seguidores > 0 else 0,
        'completada': simulacion.completada,
        'seguidores': [
            {
                'username': s.nombre_usuario,
                'sexo': s.sexo,
                'edad': s.edad,
                'region': s.region,
                'comentario': s.comentario,
                'fecha': format_chile_time(s.fecha_creacion, '%H:%M:%S')
            } for s in seguidores
        ],
        'publicaciones': [
            {
                'texto': p.texto,
                'vistos': p.vistos,
                'likes': p.likes,
                'fecha': format_chile_time(p.fecha_creacion, '%H:%M:%S')
            } for p in publicaciones
        ],
        'estadisticas': {
            'seguidores_total': estadisticas.seguidores_total if estadisticas else 0,
            'seguidores_hoy': estadisticas.seguidores_hoy if estadisticas else 0,
            'publicaciones_total': estadisticas.publicaciones_total if estadisticas else 0,
            'publicaciones_hoy': estadisticas.publicaciones_hoy if estadisticas else 0
        } if estadisticas else {}
    })

@app.route('/buscar_seguidores/<int:id>', methods=['GET'])
def buscar_seguidores(id):
    """Busca seguidores reales basados en filtros."""
    # Obtener parámetros de búsqueda
    termino = request.args.get('termino', '')
    sexo = request.args.get('sexo', '')
    edad = request.args.get('edad', '')
    region = request.args.get('region', '')
    
    # Obtener la simulación
    simulacion = Simulacion.query.get_or_404(id)
    
    # Iniciar la consulta base
    query = Seguidor.query.filter_by(simulacion_id=id)
    
    # Aplicar filtros si existen
    if termino:
        query = query.filter(Seguidor.nombre_usuario.ilike(f'%{termino}%') | 
                            Seguidor.comentario.ilike(f'%{termino}%'))
    if sexo:
        query = query.filter(Seguidor.sexo == sexo)
    if edad:
        query = query.filter(Seguidor.edad == edad)
    if region:
        query = query.filter(Seguidor.region == region)
    
    # Ejecutar la consulta y ordenar por fecha de creación (más recientes primero)
    seguidores = query.order_by(Seguidor.fecha_creacion.desc()).all()
    
    # Preparar la respuesta JSON
    resultado = []
    for seguidor in seguidores:
        resultado.append({
            'id': seguidor.id,
            'nombre_usuario': seguidor.nombre_usuario,
            'sexo': seguidor.sexo,
            'edad': seguidor.edad,
            'region': seguidor.region,
            'comentario': seguidor.comentario,
            'fecha_creacion': format_chile_time(seguidor.fecha_creacion, '%d-%m-%Y %H:%M:%S')
        })
    
    return jsonify({
        'simulacion_id': id,
        'total_resultados': len(resultado),
        'seguidores': resultado
    })

def ejecutar_simulacion(simulacion_id):
    """Ejecuta la simulación en un hilo separado. Versión simplificada."""
    global simulation_active
    
    try:
        # Configurar OpenAI
        configurar_openai()
        conectar_con_ia()
        
        # Obtener la simulación
        with app.app_context():
            simulacion = Simulacion.query.get(simulacion_id)
            if not simulacion:
                print(f"No existe la simulación con ID {simulacion_id}")
                simulation_active = False
                return
            
            if simulacion.completada:
                print(f"La simulación {simulacion_id} ya está completada")
                simulation_active = False
                return
            
            objetivo_seguidores = simulacion.objetivo_seguidores
            
            # Filtrar demografía si está configurada
            regiones_objetivo = json.loads(simulacion.regiones_objetivo) if simulacion.regiones_objetivo else REGIONES
            edades_objetivo = json.loads(simulacion.edades_objetivo) if simulacion.edades_objetivo else EDADES
            sexos_objetivo = json.loads(simulacion.sexos_objetivo) if simulacion.sexos_objetivo else SEXOS
            
            # Inicializar contador de seguidores
            seguidores = simulacion.seguidores_alcanzados
            
            # Crear estadísticas iniciales
            estadisticas = Estadistica(
                simulacion_id=simulacion_id,
                seguidores_total=seguidores,
                seguidores_hoy=0,
                publicaciones_total=0,
                publicaciones_hoy=0,
                fecha=datetime.datetime.now()
            )
            db.session.add(estadisticas)
            db.session.commit()
            
            # Bucle principal - Versión simplificada
            while seguidores < objetivo_seguidores and simulation_active:
                with app.app_context():
                    # Elegir demografía aleatoria
                    sexo = random.choice(sexos_objetivo)
                    edad = random.choice(edades_objetivo)
                    region = random.choice(regiones_objetivo)
                    
                    # Generar datos del seguidor
                    nombre_usuario = generar_nombre_usuario(sexo)
                    comentario = generar_comentario(edad, region, sexo)
                    
                    # Guardar seguidor en la base de datos
                    seguidor = Seguidor(
                        simulacion_id=simulacion_id,
                        nombre_usuario=nombre_usuario,
                        sexo=sexo,
                        edad=edad,
                        region=region,
                        comentario=comentario,
                        fecha_creacion=datetime.datetime.now()
                    )
                    db.session.add(seguidor)
                    
                    # Actualizar contadores
                    seguidores += 1
                    
                    # Actualizar estadísticas
                    estadisticas.seguidores_total = seguidores
                    estadisticas.seguidores_hoy += 1
                    
                    # Actualizar modelo de simulación
                    simulacion.seguidores_alcanzados = seguidores
                    
                    # Si alcanzamos el objetivo, marcar como completada
                    if seguidores >= objetivo_seguidores:
                        simulacion.completada = True
                        simulacion.fecha_fin = datetime.datetime.now()
                    
                    # Calcular distribuciones cada 10 seguidores
                    if seguidores > 0 and seguidores % 10 == 0:
                        # Obtener todos los seguidores
                        todos_seguidores = Seguidor.query.filter_by(simulacion_id=simulacion_id).all()
                        
                        # Calcular distribuciones
                        dist_sexo = {}
                        dist_edad = {}
                        dist_region = {}
                        
                        for s in todos_seguidores:
                            dist_sexo[s.sexo] = dist_sexo.get(s.sexo, 0) + 1
                            dist_edad[s.edad] = dist_edad.get(s.edad, 0) + 1
                            dist_region[s.region] = dist_region.get(s.region, 0) + 1
                        
                        # Actualizar estadísticas con las distribuciones
                        estadisticas.distribucion_sexo = json.dumps(dist_sexo)
                        estadisticas.distribucion_edad = json.dumps(dist_edad)
                        estadisticas.distribucion_region = json.dumps(dist_region)
                    
                    db.session.commit()
                
                # Pausa para no sobrecargar la CPU
                time.sleep(0.5)
        
        # Marcar la simulación como inactiva al finalizar
        simulation_active = False
        
    except Exception as e:
        print(f"Error en la simulación: {e}")
        simulation_active = False