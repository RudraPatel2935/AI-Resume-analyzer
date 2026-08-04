from flask import Blueprint, render_template
from flask_login import login_required

from models.analysis import Analysis


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/results/<int:analysis_id>")
@login_required
def results(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    interview_questions = [
        f"Explain your experience with {skill}."
        for skill in (analysis.missing_skills or "").split(", ")
        if skill
    ]
    return render_template("result.html", analysis=analysis, interview_questions=interview_questions)