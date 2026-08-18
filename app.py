from flask import Flask, render_template, session, redirect, url_for
from config import PORT, SECRET_KEY

# Importación de módulos creados en la carpeta /modules
from modules.auth import auth_bp
from modules.chats import chats_bp
from modules.statuses import statuses_bp
from modules.contacts import contacts_bp
from modules.settings import settings_bp

# Inicialización de la aplicación Flask configurando explícitamente las carpetas de plantillas y archivos estáticos
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = SECRET_KEY
    
# Registro de Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chats_bp)
app.register_blueprint(statuses_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(settings_bp)

@app.route('/')
def index():
    # Si ya hay una sesión activa, redirige automáticamente al chat
    if 'user' in session:
        return redirect('/chats')
    
    # Muestra la pantalla de autenticación (Login / Registro) por defecto
    return render_template('auth.html')

# Inicialización de contexto de base de datos para asegurar la creación automática de tablas (como 'novedades')
with app.app_context():
    try:
        import modules.statuses as statuses_module
        if hasattr(statuses_module, 'db'):
            statuses_module.db.create_all()
    except Exception as db_error:
        print(f"Aviso del sistema de base de datos: {db_error}")

if __name__ == '__main__':
    print(f"🚀 Servidor Modular Spatial Network ejecutándose en el puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
    
