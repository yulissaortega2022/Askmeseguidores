import os
import random
import time
import datetime
import threading
from openai import OpenAI

# Clave de API de OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "TU_OPENAI_API_KEY")

# Datos demográficos
EDADES = ["18-24 años", "25-34 años", "35-44 años", "45-54 años", "55-64 años"]
SEXOS = ["Hombre", "Mujer"]
REGIONES = [
    "Región Metropolitana", "Valparaíso", "Biobío", "La Araucanía", "Antofagasta", 
    "Coquimbo", "Los Lagos", "Maule", "O'Higgins", "Tarapacá", "Los Ríos", 
    "Arica y Parinacota", "Magallanes", "Atacama", "Ñuble", "Aysén"
]

# Nombres chilenos populares para generar nombres de usuario
NOMBRES_HOMBRE = [
    "Matías", "Sebastián", "Benjamín", "Vicente", "Martín", "Diego", "Joaquín", 
    "Felipe", "Tomás", "Agustín", "José", "Francisco", "Ignacio", "Nicolás", 
    "Cristóbal", "Lucas", "Manuel", "Maximiliano", "Rodrigo", "Alejandro"
]
NOMBRES_MUJER = [
    "Sofía", "Antonia", "Isidora", "Florencia", "Catalina", "Javiera", "Trinidad", 
    "Constanza", "Fernanda", "Emilia", "Valentina", "Victoria", "Francisca", 
    "Antonella", "Amanda", "Magdalena", "Josefa", "Camila", "Martina", "Laura"
]
APELLIDOS = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva", 
    "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López", "Fuentes", "Hernández", 
    "Torres", "Araya", "Flores", "Espinoza", "Valenzuela", "Castillo", "Tapia", 
    "Reyes", "Gutiérrez", "Castro", "Vargas", "Álvarez", "Vásquez", "Sánchez", "Fernández"
]

# Configuración del cliente OpenAI
client = None

def configurar_openai():
    """Configura el cliente de OpenAI."""
    global client
    try:
        # Si no hay API key o es la placeholder, seguimos sin intentar conectar
        if OPENAI_API_KEY == "TU_OPENAI_API_KEY":
            print("Usando modo de simulación sin conexión a OpenAI (datos ficticios)")
            client = None
            return True
            
        client = OpenAI(api_key=OPENAI_API_KEY)
        return True
    except Exception as e:
        print(f"Error al configurar OpenAI: {str(e)}")
        client = None
        # Aún retornamos True para continuar en modo de simulación
        return True

def conectar_con_ia():
    """Intenta conectar con la API de OpenAI o continúa en modo simulación."""
    print("Conectando con la IA...")
    
    # Si no hay cliente configurado, usamos datos ficticios
    if client is None:
        print("Usando datos ficticios para la simulación (sin conexión a OpenAI)")
        return True
        
    try:
        # Realizamos una petición de prueba para verificar la conexión
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Volvemos a usar un modelo compatible
            messages=[{"role": "user", "content": "Hola, esto es una prueba de conexión."}],
            max_tokens=5
        )
        print("Conexión establecida. Procesando...")
        return True
    except Exception as e:
        print(f"""
Error: no se pudo conectar con la IA.
Causa: {str(e)}.
Solución: revisa tu clave de OpenAI y tu conexión a Internet.
        """)
        print("Continuando en modo simulación con datos ficticios...")
        return True

def generar_nombre_usuario(sexo):
    """Genera un nombre de usuario aleatorio basado en el sexo."""
    if sexo == "Hombre":
        nombre = random.choice(NOMBRES_HOMBRE)
    else:
        nombre = random.choice(NOMBRES_MUJER)
    
    apellido = random.choice(APELLIDOS)
    
    # Generar un username estilo Instagram
    formatos = [
        f"{nombre.lower()}{apellido.lower()}",
        f"{nombre.lower()}_{apellido.lower()}",
        f"{nombre.lower()}.{apellido.lower()}",
        f"{nombre.lower()}{random.randint(1, 999)}",
        f"{nombre.lower()}{apellido.lower()}{random.randint(1, 99)}",
        f"real_{nombre.lower()}",
        f"{nombre.lower()}_cl",
        f"{nombre.lower()}_{random.randint(1990, 2005)}"
    ]
    
    return random.choice(formatos)

def generar_comentario(edad, region, sexo):
    """Genera un comentario usando la API de OpenAI o comentarios ficticios si la API no está disponible."""
    # Lista de comentarios ficticios por si la API no está disponible
    comentarios_ficticios = [
        f"¡Me encanta la ropa para perros! Mis peluditos en {region} siempre están a la moda. 🐕❤️",
        f"Como {sexo} de {region}, encuentro que estas prendas caninas son lo mejor para mi mascota.",
        f"Con {edad}, valoro mucho encontrar tiendas que entiendan lo que nuestros perritos necesitan. ¡Seguiré comprando aquí!",
        f"Nunca pensé que la ropa para perros pudiera ser tan linda. Mi chihuahua se ve increíble con sus nuevos outfits.",
        f"En {region} todos admiran a mi perrito cuando sale con su nueva chamarra. ¡Gracias por estos diseños únicos!",
        f"A mis {edad} he visto muchas tiendas, pero ninguna con diseños tan originales para nuestros amigos de cuatro patas.",
        f"Como {sexo} apasionado/a por las mascotas, aprecio la calidad de estas prendas. ¡Mi golden retriever luce espectacular!",
        f"Encontrar ropa que le quede bien a mi bulldog francés era imposible hasta que descubrí esta cuenta. ¡Ya no compro en otro lado!",
        f"Desde {region} quiero decirles que sus diseños son perfectos para el clima que tenemos aquí. ¡Mi perrito ya no tiembla de frío!",
        f"Con {edad}, me encanta consentir a mi mascota, y estas prendas son perfectas para hacerlo sentir especial."
    ]
    
    try:
        if OPENAI_API_KEY == "TU_OPENAI_API_KEY" or not client:
            # Si no hay API key configurada, usar comentarios ficticios
            return random.choice(comentarios_ficticios)
            
        prompt = f"Crea un comentario amigable, atractivo y emocional para una persona que tiene entre {edad}, vive en {region}, es de sexo {sexo} y ama la ropa para perros. Tono cercano y simpático, sin vender directamente, con conexión emocional. Máximo 2 frases."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Volvemos a usar un modelo compatible
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error al generar comentario: {str(e)}")
        return random.choice(comentarios_ficticios)

def generar_texto_publicacion(edad, region, sexo):
    """Genera un texto para publicación usando la API de OpenAI o textos ficticios si la API no está disponible."""
    # Lista de textos ficticios para publicaciones
    textos_publicacion = [
        f"✨ ¡{sexo}s de {region} con {edad}! Viste a tu peludito con nuestra nueva colección y haz que destaque en cada paseo. ¡Síguenos para más! 🐾",
        f"🐶 Porque tu mejor amigo merece verse como tú: con estilo. Nueva colección para {sexo}s de {edad} que aman a sus mascotas en {region}. ¡Síguenos!",
        f"¿Frío en {region}? Nuestros abriguitos para perros son tendencia entre {sexo}s de {edad}. ¡Dale estilo a tu compañero peludo! 👑🐕",
        f"Diseños únicos que enamoran a {sexo}s de {edad} en {region}. Tu perrito merece verse increíble en cada paseo. ¡Síguenos para más novedades! 🎀",
        f"Los perritos más estilosos de {region} usan nuestra ropa. Especial para {sexo}s de {edad} que consienten a sus mascotas. ¡Dale amor con estilo! ❤️",
        f"¿{sexo} amante de los perros en {region}? Tenemos los diseños que tu mascota necesita. Calidad y estilo a cada paso. ¡Síguenos! 🦮",
        f"Moda canina exclusiva para {sexo}s de {edad} en {region}. Porque tu perrito merece ser tendencia. ¡Descubre nuestra nueva colección! 🐕‍🦺",
        f"Amor por las mascotas + diseño de calidad = La marca favorita de {sexo}s de {edad} en {region}. ¡Síguenos para novedades semanales! 🛍️",
        f"En {region} los perritos más cool siguen nuestro estilo. Ideal para {sexo}s de {edad} que aman consentir a sus mascotas. ¡Únete! 🌟",
        f"Ropa que hará que tu perrito reciba cumplidos en cada paseo por {region}. {sexo}s de {edad}, ¡esto es para ustedes! 📸"
    ]
    
    try:
        if OPENAI_API_KEY == "TU_OPENAI_API_KEY" or not client:
            # Si no hay API key configurada, usar textos ficticios
            return random.choice(textos_publicacion)
            
        prompt = f"Escribe un copy inspirador de hasta 150 caracteres para un Reel sobre moda canina, dirigido a {edad}, {sexo} en {region}, invitándolos a seguir la cuenta."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Volvemos a usar un modelo compatible
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error al generar texto para publicación: {str(e)}")
        return random.choice(textos_publicacion)