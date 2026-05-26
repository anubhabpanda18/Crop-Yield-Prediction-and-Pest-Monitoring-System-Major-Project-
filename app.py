from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from routes.prediction import predict_bp
from routes.monitoring import monitor_bp
from models.crop_model import crop_model


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(predict_bp)
    app.register_blueprint(monitor_bp)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status":        "ok",
            "model_trained": crop_model.is_trained,
            "version":       "1.0.0"
        })

    @app.route("/")
    @app.route("/<path:path>")
    def frontend(path="index.html"):
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Route not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 55)
    print("  🌾 Crop Yield Prediction & Pest Monitoring System")
    print("=" * 55)

    if not crop_model.load():
        print("  ⚙️  No saved model found — training on sample data...")
        try:
            metrics = crop_model.train()
            print(f"  ✅ Models trained successfully:")
            print(f"     Yield R²: {metrics['yield_model']['r2_score']}")
        except Exception as e:
            print(f"  ❌ Training error: {e}")
    else:
        print("  ✅ Models loaded from disk.")

    print("  🚀 Server running at http://localhost:5000")
    print("=" * 55)
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)