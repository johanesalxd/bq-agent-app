"""
Probe which Python libraries are available in Vertex AI Code Interpreter.

Uses the Vertex AI Extensions API directly to execute a library probe
in the Code Interpreter extension. Run from repo root:

    uv run python setup/probe_code_interpreter.py

Note: vertexai is always initialised with the extension's home location
(us-central1), regardless of GOOGLE_CLOUD_LOCATION in the environment,
because Code Interpreter extensions are regional resources.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

import vertexai  # noqa: E402
from vertexai.extensions._extensions import Extension  # noqa: E402

_PROBE_CODE = """
candidates = {
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "seaborn": "seaborn",
    "sklearn": "sklearn",
    "statsmodels": "statsmodels",
    "PIL": "PIL",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
    "plotly": "plotly",
    "json": "json",
    "csv": "csv",
    "datetime": "datetime",
    "io": "io",
    "math": "math",
    "re": "re",
}

print("=== Code Interpreter Library Probe ===")
for display, lib in candidates.items():
    try:
        mod = __import__(lib)
        version = getattr(mod, "__version__", "stdlib")
        print(f"  {display:<15} AVAILABLE   v{version}")
    except ImportError:
        print(f"  {display:<15} NOT AVAILABLE")
print("======================================")
"""


def main() -> None:
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    extension_name = os.environ["CODE_INTERPRETER_EXTENSION_NAME"]

    # Extensions are us-central1 regional resources; use that explicitly
    # regardless of GOOGLE_CLOUD_LOCATION to avoid location mismatch errors.
    extension_location = "us-central1"

    vertexai.init(project=project_id, location=extension_location)

    print(f"Project  : {project_id}")
    print(f"Extension: {extension_name}")
    print("Running library probe...\n")

    ext = Extension(extension_name)
    response = ext.execute(
        operation_id="generate_and_execute",
        operation_params={"query": _PROBE_CODE},
    )

    result = response.get("execution_result", "")
    error = response.get("execution_error", "")

    if result:
        print(result)
    if error:
        print(f"Execution error:\n{error}")


if __name__ == "__main__":
    main()
