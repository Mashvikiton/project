import io
import traceback
import contextlib
import base64
from typing import Dict, Any, List

from db import get_student_dataset
import matplotlib.pyplot as plt


class CodeExecutor:
    def __init__(self):
        self.safe_globals = self._build_safe_globals()

    def _build_safe_globals(self) -> Dict[str, Any]:
        import pandas as pd
        import numpy as np

        return {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "float": float,
                "int": int,
                "str": str,
            },
            "pd": pd,
            "np": np,
            "plt": plt,
        }

    def _capture_plots(self) -> List[str]:
        images = []

        figs = [plt.figure(n) for n in plt.get_fignums()]

        for fig in figs:
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)

            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            images.append(img_base64)

            buf.close()

        plt.close("all")
        return images

    def execute(self, code: str, student_id: int = None) -> Dict[str, Any]:
        stdout_buffer = io.StringIO()
        error_output = None
        plots = []

        # ВАЖНО: один общий namespace
        exec_env = dict(self.safe_globals)

        try:
            # загружаем df
            if student_id is not None:
                df = get_student_dataset(student_id)
                if df is not None:
                    exec_env["df"] = df
                else:
                    exec_env["df"] = None  # важно, чтобы не было NameError

            with contextlib.redirect_stdout(stdout_buffer):
                exec(code, exec_env, exec_env)

        except Exception:
            error_output = traceback.format_exc()

        try:
            plots = self._capture_plots()
        except Exception:
            plots = []

        return {
            "stdout": stdout_buffer.getvalue(),
            "error": error_output,
            "plots": plots,
        }