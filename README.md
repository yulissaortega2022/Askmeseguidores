# SimulaGram - Simulador de Seguidores de Instagram

SimulaGram es una aplicación web que simula la obtención de seguidores en Instagram para tiendas de ropa para perros en Chile, segmentados por datos demográficos como edad, sexo y región.

## Características

- **Simulación de Seguidores**: Genera seguidores ficticios con perfiles demográficos realistas
- **Generación de Contenido**: Crea comentarios y textos para publicaciones usando IA o datos ficticios
- **Dashboard Interactivo**: Visualiza estadísticas y progreso de tus simulaciones
- **Configuración Personalizada**: Define tus propios segmentos demográficos objetivo
- **Análisis de Audiencia**: Visualiza la distribución demográfica de tus seguidores

## Tecnologías Utilizadas

- Python 3.11
- Flask (Framework web)
- SQLAlchemy (ORM para base de datos)
- PostgreSQL (Base de datos)
- OpenAI API (Generación de texto con IA)
- Chart.js (Visualización de datos)
- Bootstrap (Interfaz de usuario)

## Requisitos

- Python 3.11 o superior
- PostgreSQL
- Clave API de OpenAI (opcional)

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/simulagram.git
   cd simulagram
   ```

2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   - `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL
   - `OPENAI_API_KEY`: Clave API de OpenAI (opcional)
   - `FLASK_SECRET_KEY`: Clave secreta para Flask

4. Iniciar la aplicación:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación
- `app.py`: Configuración principal de Flask y definición de rutas
- `models.py`: Modelos de datos SQLAlchemy
- `simulador.py`: Funciones para la simulación y generación de datos
- `templates/`: Archivos HTML para la interfaz web
  - `base.html`: Plantilla base con elementos comunes
  - `index.html`: Página principal
  - `dashboard.html`: Panel de control con estadísticas
  - `configuracion.html`: Configuración de nuevas simulaciones
  - `simulacion.html`: Visualización de simulación en tiempo real
  - `analisis.html`: Análisis detallado de una simulación

## Modo Sin Conexión

Si no se proporciona una clave API de OpenAI válida, la aplicación utilizará automáticamente datos ficticios generados localmente, permitiendo que la simulación funcione sin necesidad de conexión con la API externa.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo `LICENSE` para más detalles.

## Autor

Tu Nombre - [tu-correo@ejemplo.com](mailto:tu-correo@ejemplo.com)

---

Desarrollado con ❤️ usando Python y Flask.