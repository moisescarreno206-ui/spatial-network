from flask import Flask, render_template
from config import PORT, SECRET_KEY

# Importación de módulos creados en la carpeta /modules
from modules.auth import auth_bp
from modules.chats import chats_bp
from modules.statuses import statuses_bp
from modules.contacts import contacts_bp
from modules.settings import settings_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Registro de Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chats_bp)
app.register_blueprint(statuses_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(settings_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print(f"🚀 Servidor Modular Spatial Network ejecutándose en el puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
    
