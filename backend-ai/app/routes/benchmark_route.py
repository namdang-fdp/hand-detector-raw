from flask import Blueprint, jsonify
from flasgger import swag_from
import json, os

benchmark_bp = Blueprint("benchmark_bp", __name__)

BENCHMARK_PATH = "app/models/model_benchmark.json"

@swag_from({
    "tags": ["Model Benchmark"],
    "summary": "Get model benchmark results",
    "description": "Retrieve accuracy, precision, recall, F1-score and training time for all trained models.",
    "responses": {
        200: {
            "description": "Benchmark results retrieved successfully",
            "examples": {
                "application/json": {
                    "status": "success",
                    "message": "Benchmark results retrieved successfully",
                    "data": {
                        "benchmark_results": [
                            {"model": "RandomForest (Calibrated)", "accuracy": 0.98, "f1": 0.97},
                            {"model": "Logistic Regression (L1)", "accuracy": 0.96, "f1": 0.95}
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Benchmark file not found",
            "examples": {
                "application/json": {"error": "Benchmark file not found"}
            }
        }
    }
})
@benchmark_bp.route("/benchmark", methods=["GET"])
def get_benchmark_results():
    if not os.path.exists(BENCHMARK_PATH):
        return jsonify({"error": "Benchmark file not found"}), 404

    with open(BENCHMARK_PATH, "r") as f:
        data = json.load(f)

    return jsonify({
        "status": "success",
        "message": "Benchmark results retrieved successfully",
        "data": data
    })
