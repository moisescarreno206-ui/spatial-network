import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 🔗 ENLACE AL SERVIDOR 1 (CENTRO MAESTRO AMITI OS)
SERVIDOR_1_URL = os.environ.get("SERVIDOR_1_URL", "https://tu-amiti-core.onrender.com")
TOKEN_ENLACE = os.environ.get("TOKEN_ENLACE", "AMITI_LINK_SECURE_KEY_2026")

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "short_name": "SpatialNet",
        "name": "Spatial Social Network",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/2097/2097276.png",
                "type": "image/png",
                "sizes": "192x192"
            }
        ],
        "start_url": "/",
        "background_color": "#0d0e15",
        "theme_color": "#8b5cf6",
        "display": "standalone"
    })

@app.route("/")
def portada():
    html_publico = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spatial Network</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: radial-gradient(circle at top, #1a1c2e, #0d0e15); color: #ffffff; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 30px; width: 100%; max-width: 400px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); text-align: center; }
        h1 { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
        p.sub { font-size: 0.85rem; color: #94a3b8; margin-bottom: 25px; }
        
        .tabs { display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 10px; background: none; border: none; color: #94a3b8; font-size: 0.95rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: 0.3s; }
        .tab-btn.active { color: #a855f7; border-bottom-color: #a855f7; }
        
        .form-group { margin-bottom: 15px; text-align: left; }
        label { font-size: 0.8rem; color: #cbd5e1; display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 10px; color: #fff; font-size: 0.95rem; outline: none; }
        input:focus { border-color: #a855f7; }
        
        button.btn-submit { width: 100%; padding: 12px; background: linear-gradient(135deg, #8b5cf6, #6366f1); border: none; border-radius: 10px; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); }
    </style>
</head>
<body>
    <div class="card">
        <h1>SPATIAL NETWORK</h1>
        <p class="sub">Red Social y Transmisión Multimedia Global</p>
        
        <div class="tabs">
            <button class="tab-btn active" id="tab-login" onclick="setModo('login')">Ingresar</button>
            <button class="tab-btn" id="tab-reg" onclick="setModo('reg')">Registrarse</button>
        </div>

        <form onsubmit="procesarAuth(event)">
            <div class="form-group" id="grp-user" style="display:none;">
                <label>Nombre de usuario</label>
                <input type="text" id="username" placeholder="@usuario">
            </div>
            <div class="form-group">
                <label>Correo electrónico</label>
                <input type="email" id="email" placeholder="usuario@espacio.com" required>
            </div>
            <div class="form-group">
                <label>Contraseña</label>
                <input type="password" id="password" placeholder="••••••••" required>
            </div>
            <button class="btn-submit" type="submit" id="btn-text">Ingresar a la Red</button>
        </form>
    </div>

    <script>
        let modo = 'login';
        function setModo(m) {
            modo = m;
            document.getElementById('tab-login').classList.toggle('active', m === 'login');
            document.getElementById('tab-reg').classList.toggle('active', m === 'reg');
            document.getElementById('grp-user').style.display = m === 'reg' ? 'block' : 'none';
            document.getElementById('btn-text').innerText = m === 'reg' ? 'Crear Cuenta' : 'Ingresar a la Red';
        }

        function procesarAuth(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const username = document.getElementById('username').value;

            fetch('/api/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ modo, email, password, username })
            })
            .then(r => r.json())
            .then(data => {
                if (data.exito) {
                    alert("Acceso concedido a Spatial Network");
                } else {
                    alert(data.mensaje || "Error al autenticar");
                }
            });
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_publico)

# 📡 REENVÍO SEGURO AL SERVIDOR 1
@app.route("/api/auth", methods=["POST"])
def auth_proxy():
    datos = request.json or {}
    try:
        headers = {"X-Amiti-Auth": TOKEN_ENLACE}
        res = requests.post(f"{SERVIDOR_1_URL}/api/v1/auditar_y_procesar", json=datos, headers=headers, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception:
        return jsonify({"exito": False, "mensaje": "Servicio temporalmente en mantenimiento"}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
