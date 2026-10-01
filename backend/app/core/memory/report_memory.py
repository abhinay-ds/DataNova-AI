from dataclasses import dataclass, field

@dataclass
class ReportMemory:
    latest_report = None
    report_history: list = field(default_factory=list)