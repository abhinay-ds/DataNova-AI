import pandas as pd

from app.services.report_service import ReportService
from app.services.report_export_service import ReportExportService


df = pd.DataFrame({
    "Age": [25, 30, 35],
    "Experience": [2, 5, 10],
    "Salary": [30000, 45000, 70000],
})


report_response = ReportService.generate(df)

if not report_response.success:

    print(
        "Report generation failed:",
        report_response.message
    )

    raise SystemExit


export_response = (
    ReportExportService.export_html(
        report_response.data
    )
)

print(
    "Success:",
    export_response.success
)

print(
    "Message:",
    export_response.message
)

print(
    "Data:",
    export_response.data
)