"""
Cognitive Health Report Generator
Creates downloadable PDF reports for families
Uses Foxit PDF Services API (HTML → PDF) as primary path
Falls back to Foxit Document Generation API or mock PDF
"""

import logging
from datetime import datetime, UTC, date
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates cognitive health reports as PDFs
    Combines data from Sanity with Foxit PDF generation
    """

    def __init__(self, data_store, foxit_client, pdf_services_client=None):
        """
        Args:
            data_store: DataStore instance (SanityDataStore or InMemoryDataStore)
            foxit_client: FoxitClient instance (Document Generation API)
            pdf_services_client: FoxitPDFServicesClient instance (PDF Services API)
        """
        self.data_store = data_store
        self.foxit_client = foxit_client
        self.pdf_services = pdf_services_client

    async def generate_cognitive_report(
        self,
        patient_id: str,
        days: int = 30
    ) -> bytes:
        """
        Generate comprehensive cognitive health report PDF

        Args:
            patient_id: Patient identifier
            days: Number of days to include in report (default 30)

        Returns:
            PDF bytes ready for download
        """
        logger.info(f"Generating cognitive report for {patient_id} ({days} days)")

        # 1. Fetch patient data
        patient = await self.data_store.get_patient(patient_id)
        if not patient:
            logger.error(f"Patient not found: {patient_id}")
            return self._error_pdf("Patient not found")

        # 2. Fetch cognitive trends
        trends = await self.data_store.get_cognitive_trends(patient_id, days)

        # 3. Fetch baseline
        baseline = await self.data_store.get_cognitive_baseline(patient_id)

        # 4. Fetch recent alerts
        alerts = await self.data_store.get_alerts(patient_id, limit=10)

        # 5. Fetch recent conversations
        conversations = await self.data_store.get_conversations(patient_id, limit=10)

        # 6. Calculate summary statistics
        cognitive_score = self._calculate_overall_score(trends, baseline)
        trend_direction = self._calculate_trend_direction(trends)

        # 7. Assemble template data
        template_data = {
            "patient_name": patient.get("name", "Unknown"),
            "patient_age": patient.get("age", "Unknown"),
            "report_date": date.today().isoformat(),
            "report_period_days": days,
            "cognitive_score": cognitive_score,
            "trend": trend_direction,

            # Baseline metrics
            "baseline_vocabulary": baseline.get("vocabulary_diversity", 0) if baseline else 0,
            "baseline_coherence": baseline.get("topic_coherence", 0) if baseline else 0,
            "baseline_established": baseline.get("established", False) if baseline else False,

            # Current averages
            "avg_vocabulary": self._average_metric(trends, "vocabulary_diversity"),
            "avg_coherence": self._average_metric(trends, "topic_coherence"),
            "avg_repetition": self._average_metric(trends, "repetition_rate"),

            # Alert summary
            "total_alerts": len(alerts),
            "high_severity_alerts": len([a for a in alerts if a.get("severity") == "high"]),
            "alerts": alerts,

            # Conversation summary
            "total_conversations": len(conversations),

            # Recommendations
            "recommendations": self._generate_recommendations(trends, alerts, baseline),
        }

        # 8. Try PDF Services API first (HTML → PDF) ─ primary path
        if self.pdf_services:
            try:
                html = self._build_html_report(template_data)
                pdf_bytes = await self.pdf_services.html_to_pdf(html)
                if pdf_bytes:
                    logger.info(f"✓ Report via PDF Services ({len(pdf_bytes)} bytes)")
                    return pdf_bytes
            except Exception as e:
                logger.warning(f"PDF Services failed, falling back: {e}")

        # 9. Fallback — Document Generation API (DOCX template → PDF)
        pdf_bytes = await self.foxit_client.generate_cognitive_report_pdf(
            patient_data=template_data
        )

        logger.info(f"Report generated ({len(pdf_bytes)} bytes)")
        return pdf_bytes

    # ── HTML Report Builder ─────────────────────────────────

    def _build_html_report(self, data: Dict[str, Any]) -> str:
        """Build a ClaraCare-branded HTML report for PDF conversion."""

        score = data["cognitive_score"]
        trend = data["trend"]

        # Color coding
        if score >= 70:
            score_color = "#22c55e"
            score_label = "Good"
        elif score >= 40:
            score_color = "#f59e0b"
            score_label = "Moderate"
        else:
            score_color = "#ef4444"
            score_label = "Needs Attention"

        trend_arrow = {"improving": "↑", "stable": "→", "declining": "↓"}.get(trend, "–")
        trend_color = {"improving": "#22c55e", "stable": "#6b7280", "declining": "#ef4444"}.get(trend, "#6b7280")

        # Build alerts rows
        alert_rows = ""
        for a in data.get("alerts", [])[:5]:
            sev = a.get("severity", "low")
            sev_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#3b82f6"}.get(sev, "#6b7280")
            alert_rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                                 background:{sev_color};margin-right:6px;"></span>
                    {sev.capitalize()}
                </td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{a.get('alert_type','')}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;color:#6b7280;font-size:12px;">
                    {a.get('description','')[:80]}
                </td>
            </tr>"""

        if not alert_rows:
            alert_rows = '<tr><td colspan="3" style="padding:12px;color:#9ca3af;text-align:center;">No alerts in this period</td></tr>'

        # Build recommendations list
        recs = data.get("recommendations", "")
        rec_items = ""
        for line in (recs.split("\n") if isinstance(recs, str) else recs):
            line = line.strip().lstrip("•").strip()
            if line:
                rec_items += f'<li style="margin-bottom:6px;">{line}</li>'
        if not rec_items:
            rec_items = '<li>Continue regular daily conversations</li>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ClaraCare Cognitive Health Report</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1f2937;
            background: #ffffff;
            line-height: 1.5;
        }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 40px 32px; }}
        .header {{
            text-align: center;
            padding-bottom: 24px;
            border-bottom: 2px solid #7c3aed;
            margin-bottom: 32px;
        }}
        .logo {{ font-size: 28px; font-weight: 700; color: #7c3aed; }}
        .subtitle {{ font-size: 13px; color: #9ca3af; margin-top: 4px; }}
        .patient-info {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 24px;
        }}
        .patient-name {{ font-size: 18px; font-weight: 600; }}
        .meta {{ font-size: 12px; color: #6b7280; }}
        .score-section {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }}
        .score-card {{
            flex: 1;
            background: #f9fafb;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .score-value {{ font-size: 32px; font-weight: 700; }}
        .score-label {{ font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }}
        .section {{ margin-bottom: 24px; }}
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: #7c3aed;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 1px solid #e5e7eb;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{
            text-align: left;
            padding: 8px 12px;
            background: #f3f4f6;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            color: #6b7280;
        }}
        .recs {{ padding-left: 20px; font-size: 13px; color: #374151; }}
        .footer {{
            margin-top: 40px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 11px;
            color: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">ClaraCare</div>
            <div class="subtitle">AI-Powered Cognitive Health Companion</div>
        </div>

        <div class="patient-info">
            <div class="patient-name">{data['patient_name']}</div>
            <div class="meta">
                Report Date: {data['report_date']}
                &nbsp;·&nbsp; Period: Last {data['report_period_days']} days
                &nbsp;·&nbsp; Conversations: {data['total_conversations']}
            </div>
        </div>

        <div class="score-section">
            <div class="score-card">
                <div class="score-value" style="color:{score_color}">{score}</div>
                <div class="score-label">Cognitive Score</div>
                <div style="font-size:12px;color:{score_color};margin-top:4px;">{score_label}</div>
            </div>
            <div class="score-card">
                <div class="score-value" style="color:{trend_color}">{trend_arrow}</div>
                <div class="score-label">Trend</div>
                <div style="font-size:12px;color:{trend_color};margin-top:4px;">{trend.capitalize()}</div>
            </div>
            <div class="score-card">
                <div class="score-value" style="color:#3b82f6">{data['total_alerts']}</div>
                <div class="score-label">Alerts</div>
                <div style="font-size:12px;color:#ef4444;margin-top:4px;">
                    {data['high_severity_alerts']} high severity
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Cognitive Metrics</div>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Current</th>
                    <th>Baseline</th>
                </tr>
                <tr>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">Vocabulary Diversity</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{data['avg_vocabulary']:.2f}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{data['baseline_vocabulary']:.2f}</td>
                </tr>
                <tr>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">Topic Coherence</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{data['avg_coherence']:.2f}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{data['baseline_coherence']:.2f}</td>
                </tr>
                <tr>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">Repetition Rate</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{data['avg_repetition']:.2f}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">–</td>
                </tr>
            </table>
        </div>

        <div class="section">
            <div class="section-title">Recent Alerts</div>
            <table>
                <tr>
                    <th>Severity</th>
                    <th>Type</th>
                    <th>Details</th>
                </tr>
                {alert_rows}
            </table>
        </div>

        <div class="section">
            <div class="section-title">Recommendations</div>
            <ul class="recs">
                {rec_items}
            </ul>
        </div>

        <div class="footer">
            <p>Generated by ClaraCare · AI-Powered Elder Care Companion</p>
            <p>This report is for informational purposes only and does not constitute medical advice.</p>
            <p>© {datetime.now().year} ClaraCare · Powered by Foxit PDF Services</p>
        </div>
    </div>
</body>
</html>"""

    # ── scoring helpers (unchanged) ─────────────────────────

    def _calculate_overall_score(self, trends: list, baseline: dict) -> int:
        """Calculate overall cognitive score (0-100)"""
        if not trends or not baseline or not baseline.get("established"):
            return 0

        recent = trends[-7:] if len(trends) >= 7 else trends

        vocab_avg = self._average_metric(recent, "vocabulary_diversity")
        coherence_avg = self._average_metric(recent, "topic_coherence")
        repetition_avg = self._average_metric(recent, "repetition_rate")

        vocab_baseline = baseline.get("vocabulary_diversity", 0.5)
        coherence_baseline = baseline.get("topic_coherence", 0.8)
        repetition_baseline = baseline.get("repetition_rate", 0.05)

        vocab_score = min(100, (vocab_avg / vocab_baseline * 100)) if vocab_baseline > 0 else 50
        coherence_score = min(100, (coherence_avg / coherence_baseline * 100)) if coherence_baseline > 0 else 50
        repetition_score = max(0, 100 - (repetition_avg / repetition_baseline * 100)) if repetition_baseline > 0 else 50

        overall = (vocab_score * 0.4 + coherence_score * 0.4 + repetition_score * 0.2)
        return int(overall)

    def _calculate_trend_direction(self, trends: list) -> str:
        """Determine if cognitive metrics are improving, stable, or declining"""
        if len(trends) < 4:
            return "insufficient_data"

        mid = len(trends) // 2
        first_half = trends[:mid]
        second_half = trends[mid:]

        vocab_first = self._average_metric(first_half, "vocabulary_diversity")
        vocab_second = self._average_metric(second_half, "vocabulary_diversity")

        coherence_first = self._average_metric(first_half, "topic_coherence")
        coherence_second = self._average_metric(second_half, "topic_coherence")

        vocab_change = (vocab_second - vocab_first) / vocab_first if vocab_first > 0 else 0
        coherence_change = (coherence_second - coherence_first) / coherence_first if coherence_first > 0 else 0

        avg_change = (vocab_change + coherence_change) / 2

        if avg_change > 0.05:
            return "improving"
        elif avg_change < -0.05:
            return "declining"
        else:
            return "stable"

    def _average_metric(self, trends: list, metric_name: str) -> float:
        """Calculate average of a metric across trends"""
        values = [t.get(metric_name) for t in trends if t.get(metric_name) is not None]
        return sum(values) / len(values) if values else 0.0

    def _generate_recommendations(
        self,
        trends: list,
        alerts: list,
        baseline: dict
    ) -> str:
        """Generate recommendations based on data"""
        recommendations = []

        high_alerts = [a for a in alerts if a.get("severity") == "high"]
        if high_alerts:
            recommendations.append("• Consult with healthcare provider about recent high-priority alerts")

        if len(trends) >= 4:
            trend = self._calculate_trend_direction(trends)
            if trend == "declining":
                recommendations.append("• Consider scheduling cognitive assessment with doctor")
                recommendations.append("• Increase engagement activities and social interaction")

        recent_repetition = self._average_metric(trends[-7:], "repetition_rate")
        if recent_repetition > 0.15:
            recommendations.append("• Monitor for repetitive storytelling patterns")

        if not recommendations:
            recommendations.append("• Continue regular daily conversations")
            recommendations.append("• Maintain current care routine")

        return "\n".join(recommendations)

    def _error_pdf(self, error_message: str) -> bytes:
        """Generate error PDF"""
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
50 700 Td
(Error: {error_message}) Tj
ET
endstream
endobj
xref
0 5
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF
"""
        return pdf_content.encode('latin-1')
