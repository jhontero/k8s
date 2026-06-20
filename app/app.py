# app.py
#
# Microservicio de ejemplo construido con Flask.
# Expone dos endpoints:
#   GET /        -> mensaje de bienvenida del microservicio
#   GET /health  -> endpoint de healthcheck, usado por Kubernetes
#                   (liveness/readiness probes) para confirmar que
#                   la aplicacion esta respondiendo correctamente.

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    """Endpoint de salud. Kubernetes lo puede usar como probe."""
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    """Endpoint principal del microservicio."""
    return jsonify({"message": "Microservicio K8S - Universidad de La Sabana"})


if __name__ == "__main__":
    # host="0.0.0.0" es obligatorio dentro del contenedor: si se deja
    # el valor por defecto (127.0.0.1), la app solo aceptaria conexiones
    # desde dentro del propio contenedor, y el Service de Kubernetes
    # no podria enrutarle trafico desde fuera.
    app.run(host="0.0.0.0", port=5000)
