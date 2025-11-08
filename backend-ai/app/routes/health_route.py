from flask import Blueprint, jsonify
from flasgger import swag_from
import os
from datetime import datetime

health_bp = Blueprint("health_bp", __name__)

@swag_from({
    "tags": ["System"],
    "summary": "Health Check Endpoint",
    "description": "Check if backend service is alive and provide environment info.",
    "responses": {
        200: {
            "description": "Service status OK",
            "examples": {
                "application/json": {
                    "status": "ok",
                    "service": "hand-detect-ai-backend",
                    "timestamp": "2025-11-07T08:12:15Z",
                    "environment": "local"
                }
            }
        }
    }
})
@health_bp.route("/healthz", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": os.getenv("SERVICE_NAME", "hand-detect-ai-backend"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": os.getenv("ENVIRONMENT", "local"),
    }), 200
