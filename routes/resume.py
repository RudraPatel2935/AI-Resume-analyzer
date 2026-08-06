import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.db import db
from models.analysis import Analysis
from models.resume import Resume
from nlp.skill_extractor import extract_skills, load_skills_database
from nlp.text_cleaner import clean_text
from parser.docx_parser import extract_text_from_docx
from parser.pdf_parser import extract_text_from_pdf
from utils.feedback_generator import generate_feedback
from ml_models.resume_classifier.predict import predict_category
from ml_models.ats_scoring.ats_model import analyze_ats


resume_bp = Blueprint("resume", __name__)


def _extract_resume_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_storage)
    if filename.endswith(".docx"):
        return extract_text_from_docx(file_storage)
    raise ValueError("Only PDF and DOCX files are supported.")


@resume_bp.route("/dashboard")
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    analyses = Analysis.query.join(Resume).filter(Resume.user_id == current_user.id).all()
    total_analyses = len(analyses)
    average_score = round(sum(a.ats_score for a in analyses) / total_analyses, 2) if analyses else 0
    latest_category = analyses[0].predicted_category if analyses else "Not available"

    return render_template(
        "dashboard.html",
        resumes=resumes,
        analyses=analyses,
        total_analyses=total_analyses,
        average_score=average_score,
        latest_category=latest_category,
    )


@resume_bp.route("/upload", methods=["POST"])
@login_required
def upload_resume():
    resume_file = request.files.get("resume_file")
    job_description = request.form.get("job_description", "").strip()

    if not resume_file or not resume_file.filename:
        flash("Please upload a resume.", "danger")
        return redirect(url_for("index"))

    if not job_description:
        flash("Please enter a job description.", "danger")
        return redirect(url_for("index"))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, resume_file.filename)
    resume_file.save(save_path)

    try:
        resume_text = _extract_resume_text(resume_file)
    except Exception as exc:
        flash(str(exc), "danger")
        return redirect(url_for("index"))

    cleaned_resume = clean_text(resume_text)
    category = predict_category(cleaned_resume)
    ats_result = analyze_ats(resume_text, job_description)
    skills_db = load_skills_database(current_app.config["SKILLS_FILE"])
    resume_skills = extract_skills(cleaned_resume, skills_db)
    missing_skills = ats_result["missing_skills"]
    feedback = generate_feedback(
        missing_skills,
        category,
        resume_text=resume_text,
        job_description=job_description,
        ats_details=ats_result,
    )

    resume_record = Resume(
        user_id=current_user.id,
        filename=resume_file.filename,
        resume_text=resume_text,
    )
    db.session.add(resume_record)
    db.session.flush()

    analysis_record = Analysis(
        resume_id=resume_record.id,
        job_description=job_description,
        ats_score=ats_result["score"],
        predicted_category=category,
        matched_skills=", ".join(ats_result["matched_skills"]),
        missing_skills=", ".join(missing_skills),
        feedback=feedback,
    )
    db.session.add(analysis_record)
    db.session.commit()

    return render_template(
        "result.html",
        analysis=analysis_record,
        resume_skills=resume_skills,
        ats_details=ats_result,
        interview_questions=generate_feedback(
            missing_skills,
            category,
            resume_text=resume_text,
            job_description=job_description,
            ats_details=ats_result,
            as_questions=True,
        ),
    )