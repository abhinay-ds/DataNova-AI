from __future__ import annotations

from pathlib import Path
from datetime import datetime
import html

from app.core.ai_engine.response import AIResponse


from app.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
reports_base = Path(settings.DATA_DIR) if settings.DATA_DIR else BACKEND_DIR
STATIC_REPORTS_DIR = reports_base / "static" / "reports"


class ReportExportService:

    REPORT_DIR = STATIC_REPORTS_DIR

    @classmethod
    def export_html(
        cls,
        report: dict,
    ) -> AIResponse:

        try:

            if not report:
                return AIResponse(
                    success=False,
                    message="Report data is empty."
                )

            cls.REPORT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            filename = (
                f"datanova_report_{timestamp}.html"
            )

            path = cls.REPORT_DIR / filename

            profile = report.get(
                "profile",
                {}
            )

            shape = profile.get(
                "shape",
                {}
            )

            quality = report.get(
                "quality",
                {}
            )

            insights = report.get(
                "insights",
                []
            )

            recommendations = report.get(
                "recommendations",
                []
            )

            model_training = report.get(
                "model_training",
                {}
            )

            model_evaluation = report.get(
                "model_evaluation",
                {}
            )

            correlation = report.get(
                "correlation",
                {}
            )

            # =================================================
            # HTML
            # =================================================

            html_content = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>DataNova AI Report</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
    background: #f4f7fb;
    color: #1f2937;
}}

.container {{
    width: 90%;
    max-width: 1100px;
    margin: 40px auto;
}}

.header {{
    background: #2563eb;
    color: white;
    padding: 35px;
    border-radius: 14px;
    margin-bottom: 25px;
}}

.header h1 {{
    margin: 0 0 10px 0;
    font-size: 32px;
}}

.header p {{
    margin: 5px 0;
}}

.section {{
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow:
        0 2px 10px rgba(0,0,0,0.06);
}}

.section h2 {{
    margin-top: 0;
    color: #1d4ed8;
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}}

.card {{
    background: #f8fafc;
    padding: 20px;
    border-radius: 10px;
}}

.card-title {{
    font-size: 14px;
    color: #64748b;
}}

.card-value {{
    font-size: 26px;
    font-weight: bold;
    margin-top: 8px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}}

th,
td {{
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
    text-align: left;
}}

th {{
    background: #eff6ff;
}}

ul {{
    line-height: 1.8;
}}

.metric {{
    font-size: 24px;
    font-weight: bold;
    color: #2563eb;
}}

.footer {{
    text-align: center;
    color: #64748b;
    margin-top: 30px;
    padding: 20px;
}}

pre {{
    background: #0f172a;
    color: #e2e8f0;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>DataNova AI</h1>

<h2>Dataset Analysis & Machine Learning Report</h2>

<p>
Generated:
{html.escape(
    str(report.get("generated_at", ""))
)}
</p>

</div>


<!-- DATASET OVERVIEW -->

<div class="section">

<h2>Dataset Overview</h2>

<div class="cards">

<div class="card">

<div class="card-title">
Rows
</div>

<div class="card-value">
{shape.get("rows", 0)}
</div>

</div>

<div class="card">

<div class="card-title">
Columns
</div>

<div class="card-value">
{shape.get("columns", 0)}
</div>

</div>

<div class="card">

<div class="card-title">
Missing Values
</div>

<div class="card-value">
{sum(
    profile.get(
        "missing_values",
        {}
    ).values()
)}
</div>

</div>

<div class="card">

<div class="card-title">
Duplicate Rows
</div>

<div class="card-value">
{profile.get("duplicates", 0)}
</div>

</div>

</div>

</div>


<!-- DATA QUALITY -->

<div class="section">

<h2>Data Quality</h2>

<div class="cards">

<div class="card">

<div class="card-title">
Quality Score
</div>

<div class="card-value">
{quality.get("score", 0)}/100
</div>

</div>

<div class="card">

<div class="card-title">
Rating
</div>

<div class="card-value">
{html.escape(
    str(
        quality.get(
            "rating",
            "Unknown"
        )
    )
)}
</div>

</div>

</div>

</div>


<!-- INSIGHTS -->

<div class="section">

<h2>Key Insights</h2>

<ul>
"""

            for insight in insights:

                html_content += f"""
<li>
{html.escape(str(insight))}
</li>
"""

            html_content += """

</ul>

</div>


<!-- RECOMMENDATIONS -->

<div class="section">

<h2>Recommendations</h2>

<ul>
"""

            for recommendation in recommendations:

                html_content += f"""
<li>
{html.escape(str(recommendation))}
</li>
"""

            html_content += """

</ul>

</div>


<!-- MODEL TRAINING -->

<div class="section">

<h2>Machine Learning</h2>

<div class="cards">

<div class="card">

<div class="card-title">
Problem Type
</div>

<div class="card-value">
"""

            html_content += html.escape(
                str(
                    model_training.get(
                        "problem_type",
                        "N/A"
                    )
                )
            )

            html_content += """

</div>

</div>

<div class="card">

<div class="card-title">
Best Model
</div>

<div class="card-value">
"""

            html_content += html.escape(
                str(
                    model_training.get(
                        "best_model",
                        "N/A"
                    )
                )
            )

            html_content += """

</div>

</div>

<div class="card">

<div class="card-title">
Target
</div>

<div class="card-value">
"""

            html_content += html.escape(
                str(
                    model_training.get(
                        "target",
                        "N/A"
                    )
                )
            )

            html_content += """

</div>

</div>

<div class="card">

<div class="card-title">
Training Score
</div>

<div class="card-value">
"""

            html_content += str(
                model_training.get(
                    "score",
                    "N/A"
                )
            )

            html_content += """

</div>

</div>

</div>


<h3>Model Comparison</h3>

<table>

<tr>

<th>Model</th>
<th>R²</th>
<th>MAE</th>
<th>RMSE</th>
<th>Cross Validation</th>

</tr>
"""

            for result in model_training.get(
                "results",
                []
            ):

                html_content += f"""

<tr>

<td>
{html.escape(
    str(result.get("model", ""))
)}
</td>

<td>
{result.get("r2", "N/A")}
</td>

<td>
{result.get("mae", "N/A")}
</td>

<td>
{result.get("rmse", "N/A")}
</td>

<td>
{result.get("cross_validation", "N/A")}
</td>

</tr>
"""

            html_content += """

</table>

</div>


<!-- MODEL EVALUATION -->

<div class="section">

<h2>Model Evaluation</h2>

<div class="cards">

<div class="card">

<div class="card-title">
R² Score
</div>

<div class="card-value">
"""

            html_content += str(
                model_evaluation.get(
                    "r2_score",
                    "N/A"
                )
            )

            html_content += """

</div>

</div>

<div class="card">

<div class="card-title">
MAE
</div>

<div class="card-value">
"""

            html_content += str(
                model_evaluation.get(
                    "mae",
                    "N/A"
                )
            )

            html_content += """

</div>

</div>

<div class="card">

<div class="card-title">
RMSE
</div>

<div class="card-value">
"""

            html_content += str(
                model_evaluation.get(
                    "rmse",
                    "N/A"
                )
            )

            html_content += """

</div>

</div>

</div>

</div>


<!-- CORRELATION -->

"""

            if correlation:

                matrix = correlation.get(
                    "correlation_matrix",
                    {}
                )

                html_content += """

<div class="section">

<h2>Correlation Analysis</h2>

<table>

<tr>
<th>Column</th>
<th>Correlations</th>
</tr>
"""

                for column, values in matrix.items():

                    html_content += f"""

<tr>

<td>
{html.escape(str(column))}
</td>

<td>
{html.escape(str(values))}
</td>

</tr>
"""

                html_content += """

</table>

</div>
"""

            html_content += """

<div class="footer">

Generated by
<strong>DataNova AI</strong>

<br>

AI-Powered Data Analysis Platform

</div>

</div>

</body>

</html>
"""

            # =================================================
            # Save
            # =================================================

            path.write_text(
                html_content,
                encoding="utf-8"
            )

            return AIResponse(

                success=True,

                message=(
                    "HTML report exported successfully."
                ),

                data={
                    "file_path": str(path),
                    "filename": filename,
                    "format": "html",
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )