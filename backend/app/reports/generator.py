"""
Cognitive Health Report Generator
Creates downloadable PDF reports for families
Uses Foxit PDF Services API (HTML → PDF) as primary path
Uses Gemini LLM for executive summary generation
Falls back to Foxit Document Generation API or mock PDF
"""

import logging
import os
from datetime import datetime, UTC, date
from typing import Dict, Any, List, Optional

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

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
            "conversations": conversations[:5],

            # Recommendations
            "recommendations": self._generate_recommendations(trends, alerts, baseline),

            # Gemini executive summary
            "executive_summary": self._generate_executive_summary(template_data_partial={
                "patient_name": patient.get("name", "Unknown"),
                "cognitive_score": cognitive_score,
                "trend": trend_direction,
                "total_alerts": len(alerts),
                "total_conversations": len(conversations),
                "avg_vocabulary": self._average_metric(trends, "vocabulary_diversity"),
                "avg_coherence": self._average_metric(trends, "topic_coherence"),
                "avg_repetition": self._average_metric(trends, "repetition_rate"),
                "conversations": conversations[:5],
                "report_period_days": days,
            }),
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

        # Human-readable alert type names
        _alert_type_labels = {
            "coherence_drop": "Coherence Drop",
            "cognitive_decline": "Cognitive Decline",
            "vocabulary_decline": "Vocabulary Decline",
            "repetition_increase": "Repetition Increase",
            "memory_inconsistency": "Memory Inconsistency",
            "distress": "Distress",
            "fall": "Fall Risk",
            "confusion": "Confusion",
            "pain": "Pain Report",
            "social_connection": "Wants Family Contact",
            "patient_request": "Patient Request",
            "medication_concern": "Medication Concern",
        }

        # Build alerts rows
        alert_rows = ""
        for a in data.get("alerts", [])[:5]:
            sev = a.get("severity", "low")
            sev_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#3b82f6"}.get(sev, "#6b7280")
            raw_type = a.get('alert_type', '')
            friendly_type = _alert_type_labels.get(raw_type, raw_type.replace('_', ' ').title())
            alert_date = a.get('timestamp', a.get('created_at', ''))[:10]
            alert_rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                                 background:{sev_color};margin-right:6px;"></span>
                    {sev.capitalize()}
                </td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{friendly_type}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;color:#6b7280;font-size:12px;">
                    {a.get('description','')}
                </td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;color:#9ca3af;font-size:11px;white-space:nowrap;">
                    {alert_date}
                </td>
            </tr>"""

        if not alert_rows:
            alert_rows = '<tr><td colspan="4" style="padding:12px;color:#9ca3af;text-align:center;">No alerts in this period</td></tr>'

        # Build conversation rows
        convo_rows = ""
        for c in data.get("conversations", []):
            date_str = c.get("timestamp", "")[:10]
            mood = c.get("detected_mood", "Neutral").capitalize()
            summary = c.get("summary", "")
            duration = f"{c.get('duration', 0)//60}m" if c.get('duration') else "-"
            convo_rows += f"""
            <tr style="page-break-inside:avoid;">
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;white-space:nowrap;">{date_str}<br><span style="color:#9ca3af;font-size:11px;">{duration}</span></td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;">{mood}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;color:#6b7280;font-size:12px;">{summary}</td>
            </tr>"""

        if not convo_rows:
            convo_rows = '<tr><td colspan="3" style="padding:12px;color:#9ca3af;text-align:center;">No recent conversations</td></tr>'

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
        @page {{ size: letter; margin: 20mm; }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1f2937;
            background: #ffffff;
            line-height: 1.5;
        }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px 32px; }}
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
            page-break-inside: avoid;
        }}
        .patient-name {{ font-size: 18px; font-weight: 600; }}
        .meta {{ font-size: 12px; color: #6b7280; }}
        .score-section {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            page-break-inside: avoid;
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
        .section {{ margin-bottom: 32px; page-break-inside: avoid; }}
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
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
        th {{
            text-align: left;
            padding: 8px 12px;
            background: #f3f4f6;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            color: #6b7280;
        }}
        td {{ word-wrap: break-word; white-space: normal; }}
        tr {{ page-break-inside: avoid; }}
        .recs {{ padding-left: 20px; font-size: 13px; color: #374151; }}
        .footer {{
            margin-top: 40px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 11px;
            color: #9ca3af;
            page-break-inside: avoid;
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
                Age: {data.get('patient_age', 'Unknown')}
                &nbsp;·&nbsp; Report Date: {data['report_date']}
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

        <div class="section" style="background:#f0fdf4;border-radius:8px;padding:16px 20px;border-left:4px solid #22c55e;">
            <div style="font-size:13px;font-weight:600;color:#166534;margin-bottom:8px;">Executive Summary</div>
            <div style="font-size:13px;color:#374151;line-height:1.7;">
                {data.get('executive_summary', 'Not enough data to generate a summary.')}
            </div>
        </div>

        <div class="section">
            <div class="section-title">Cognitive Metrics</div>
            <table>
                <tr>
                    <th style="width:40%">Metric</th>
                    <th style="width:20%">Current</th>
                    <th style="width:20%">Baseline</th>
                    <th style="width:20%">Change</th>
                </tr>
                {self._metric_row('Vocabulary Diversity', data['avg_vocabulary'], data['baseline_vocabulary'], 'Uses a range of different words')}
                {self._metric_row('Topic Coherence', data['avg_coherence'], data['baseline_coherence'], 'Stays on topic during conversation')}
                {self._metric_row('Repetition Rate', data['avg_repetition'], None, 'Repeats phrases or questions', lower_is_better=True)}
            </table>
        </div>

        <div class="section" style="background:#f9fafb;border-radius:8px;padding:16px 20px;">
            <div style="font-size:13px;font-weight:600;color:#7c3aed;margin-bottom:8px;">What These Metrics Mean</div>
            <div style="font-size:12px;color:#6b7280;line-height:1.6;">
                <strong>Vocabulary Diversity</strong> measures how many unique words are used. A decline may indicate word-finding difficulty.<br>
                <strong>Topic Coherence</strong> tracks whether conversations stay on topic. Lower scores may suggest confusion or difficulty concentrating.<br>
                <strong>Repetition Rate</strong> measures how often phrases are repeated. Higher rates can be an early sign of memory difficulty.<br>
                <em>All metrics range from 0.0 to 1.0. Scores are compared against the patient's personal baseline, not a population average.</em>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Recent Alerts</div>
            <table>
                <tr>
                    <th style="width:12%">Severity</th>
                    <th style="width:20%">Type</th>
                    <th style="width:53%">Details</th>
                    <th style="width:15%">Date</th>
                </tr>
                {alert_rows}
            </table>
        </div>

        <div class="section">
            <div class="section-title">Recent Conversations</div>
            <table>
                <tr>
                    <th style="width:20%">Date & Length</th>
                    <th style="width:20%">Mood</th>
                    <th style="width:60%">Summary</th>
                </tr>
                {convo_rows}
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

    # ── metric row helper ──────────────────────────────────────

    def _metric_row(self, name: str, current: float, baseline: float | None,
                    description: str, lower_is_better: bool = False) -> str:
        """Build one <tr> for the cognitive metrics table with change arrow."""
        cell = 'style="padding:8px 12px;border-bottom:1px solid #f3f4f6;"'

        baseline_str = f"{baseline:.2f}" if baseline else "–"

        # Change indicator
        if baseline and baseline > 0:
            diff = current - baseline
            if lower_is_better:
                diff = -diff  # for repetition, going up is bad
            if diff > 0.03:
                change_arrow = "↑"
                change_color = "#22c55e"
            elif diff < -0.03:
                change_arrow = "↓"
                change_color = "#ef4444"
            else:
                change_arrow = "→"
                change_color = "#6b7280"
        else:
            change_arrow = "–"
            change_color = "#6b7280"

        return f"""<tr>
            <td {cell}>
                <div>{name}</div>
                <div style="font-size:11px;color:#9ca3af;">{description}</div>
            </td>
            <td {cell}><strong>{current:.2f}</strong></td>
            <td {cell}>{baseline_str}</td>
            <td {cell} style="text-align:center;">
                <span style="font-size:18px;font-weight:700;color:{change_color};">{change_arrow}</span>
            </td>
        </tr>"""

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

    def _generate_executive_summary(self, template_data_partial: dict) -> str:
        """
        Generate a warm, family-friendly executive summary using Gemini LLM.
        This appears at the top of the PDF report.
        """
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key or not _GEMINI_AVAILABLE:
            return self._fallback_executive_summary(template_data_partial)

        d = template_data_partial
        convos = d.get("conversations", [])
        convo_summaries = "\n".join(
            f"  - {c.get('timestamp', '')[:10]}: {c.get('summary', 'Check-in call')} (mood: {c.get('detected_mood', 'neutral')})"
            for c in convos
        ) or "  No recent conversations available."

        prompt = f"""You are writing an executive summary for a cognitive health report about {d['patient_name']}, prepared for their family.

DATA:
- Overall cognitive score: {d['cognitive_score']}/100
- Trend: {d['trend']}
- Period: Last {d['report_period_days']} days
- Total conversations: {d['total_conversations']}
- Total alerts: {d['total_alerts']}
- Avg vocabulary diversity: {d['avg_vocabulary']:.2f}
- Avg topic coherence: {d['avg_coherence']:.2f}
- Avg repetition rate: {d['avg_repetition']:.2f}

Recent conversations:
{convo_summaries}

Write a 3-4 sentence executive summary for the family. Rules:
- Warm, non-clinical language — write like a caring nurse briefing the family
- Mention {d['patient_name']} by name
- Highlight key trends (improving/stable/declining) and what they mean practically
- If declining, be honest but compassionate — suggest next steps
- If stable/improving, be reassuring
- Do NOT mention "AI", "Clara", "companion" or technical metrics by name
- Keep under 80 words"""

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3-flash-preview")
            response = model.generate_content(prompt)
            summary = response.text.strip().strip('"').strip("'")
            logger.info(f"[GEMINI] Executive summary generated ({len(summary)} chars)")
            return summary
        except Exception as exc:
            logger.warning(f"[GEMINI] Executive summary failed: {exc}")
            return self._fallback_executive_summary(template_data_partial)

    def _fallback_executive_summary(self, data: dict) -> str:
        """Simple fallback executive summary without Gemini."""
        name = data.get("patient_name", "Your loved one")
        score = data.get("cognitive_score", 0)
        trend = data.get("trend", "stable")

        if score >= 70:
            return (f"{name}'s cognitive health looks good overall. "
                    f"Conversations have been flowing naturally with healthy engagement. "
                    f"Continue regular daily check-ins to maintain this positive trend.")
        elif score >= 40:
            return (f"{name}'s cognitive health is showing some areas worth watching. "
                    f"While most conversations are comfortable, there are a few patterns "
                    f"that may be worth discussing at the next doctor visit.")
        else:
            return (f"{name}'s recent conversations suggest some changes in cognitive patterns "
                    f"that deserve attention. Consider scheduling a conversation with "
                    f"the healthcare provider to discuss these trends.")

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
