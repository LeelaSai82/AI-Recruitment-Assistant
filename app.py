import os
import logging
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from datetime import datetime
from utils.resume_parser import extract_skills_from_resume, predict_job_role
from utils.nlp_utils import extract_skills_from_job_description, calculate_similarity
from utils.gemini_utils import generate_interview_questions

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create instance directory
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Create uploads directory
uploads_path = os.path.join(basedir, 'uploads')
os.makedirs(uploads_path, exist_ok=True)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - Use direct path for SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'recruitment.db')}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Configure upload settings
UPLOAD_FOLDER = uploads_path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Import models after db is defined
with app.app_context():
    # Import the models here
    import models
    
    # Create all tables
    db.create_all()

@app.route('/')
def index():
    """Home page with resume upload form"""
    return render_template('index.html')

@app.route('/upload_resumes', methods=['POST'])
def upload_resumes():
    """Handle resume uploads"""
    # Check if job description is provided
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        flash('Please provide a job description', 'danger')
        return redirect(url_for('index'))
    
    # Check if at least one resume is uploaded
    if 'resumes' not in request.files:
        flash('No resume files uploaded', 'danger')
        return redirect(url_for('index'))
    
    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        flash('No resume files selected', 'danger')
        return redirect(url_for('index'))
    
    # Extract skills from job description
    job_skills = extract_skills_from_job_description(job_description)
    
    # Save job description and skills in session
    session['job_description'] = job_description
    session['job_skills'] = job_skills
    
    # Process each uploaded resume
    parsed_resumes = []
    job_role_counts = {}
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract candidate information from resume
                skills = extract_skills_from_resume(filepath)
                job_role = predict_job_role(skills)
                
                # Extract candidate name from filename (assuming format: Name_Resume.pdf)
                candidate_name = filename.split('_')[0].replace('-', ' ').title()
                if '.' in candidate_name:
                    candidate_name = candidate_name.split('.')[0]
                
                # Calculate similarity score with job description
                similarity_score = calculate_similarity(skills, job_skills)
                similarity_percentage = int(similarity_score * 100)
                
                # Save to database
                resume = models.Resume(
                    filename=filename,
                    filepath=filepath,
                    candidate_name=candidate_name,
                    job_role=job_role,
                    skills=json.dumps(skills),
                    similarity_score=similarity_percentage
                )
                db.session.add(resume)
                
                # Add to parsed resumes list
                parsed_resumes.append({
                    'id': resume.id if resume.id else 0,
                    'candidate_name': candidate_name,
                    'job_role': job_role,
                    'skills': skills,
                    'similarity_score': similarity_percentage
                })
                
                # Update job role counts for analytics
                job_role_counts[job_role] = job_role_counts.get(job_role, 0) + 1
                
            except Exception as e:
                app.logger.error(f"Error processing resume {file.filename}: {str(e)}")
                flash(f'Error processing resume {file.filename}', 'danger')
    
    # Save job role counts in session for analytics
    session['job_role_counts'] = job_role_counts
    
    # Commit database changes
    db.session.commit()
    
    # Sort resumes by similarity score (descending)
    parsed_resumes.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Store in session
    session['parsed_resumes'] = parsed_resumes
    
    flash(f'Successfully processed {len(parsed_resumes)} resumes', 'success')
    return redirect(url_for('results'))

@app.route('/results')
def results():
    """Show matching results page"""
    job_description = session.get('job_description', '')
    job_skills = session.get('job_skills', [])
    
    # Get resumes from database
    resumes = models.Resume.query.order_by(models.Resume.similarity_score.desc()).all()
    
    # For each resume, parse the skills from JSON string
    for resume in resumes:
        resume.skills = json.loads(resume.skills) if resume.skills else []
    
    return render_template('results.html', 
                          resumes=resumes, 
                          job_description=job_description,
                          job_skills=job_skills)

@app.route('/generate_questions/<int:resume_id>')
def generate_questions(resume_id):
    """Generate interview questions for a specific candidate"""
    try:
        resume = models.Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        job_description = session.get('job_description', '')
        candidate_skills = json.loads(resume.skills) if resume.skills else []
        
        # Generate questions using our utility function
        questions = generate_interview_questions(
            candidate_name=resume.candidate_name,
            job_role=resume.job_role,
            skills=candidate_skills,
            job_description=job_description
        )
        
        # Log the successful generation
        app.logger.info(f"Generated {len(questions)} questions for {resume.candidate_name}")
        
        return jsonify({'questions': questions})
    
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error generating questions: {str(e)}")
        
        # Get resume job role safely
        job_role_text = "this field"
        if 'resume' in locals() and resume and resume.job_role:
            job_role_text = resume.job_role
        
        # Return generic questions as fallback
        fallback_questions = [
            f"Tell me about your background in {job_role_text}.",
            "What are your strongest technical skills?",
            "Describe a challenging project you've worked on.",
            "How do you approach problem-solving?",
            "What are your career goals?"
        ]
        
        return jsonify({'questions': fallback_questions})

@app.route('/analytics')
def analytics():
    """Show recruitment analytics dashboard"""
    job_role_counts = session.get('job_role_counts', {})
    total_resumes = sum(job_role_counts.values())
    
    # Get all resumes for more detailed analytics
    resumes = models.Resume.query.all()
    
    # Calculate average match score properly
    if resumes:
        # Already stored as percentage (0-100), no need to multiply by 100
        avg_similarity = sum([r.similarity_score for r in resumes]) / len(resumes)
    else:
        avg_similarity = 0
    
    # Create score ranges for the chart
    score_ranges = {
        '0-20%': 0,
        '21-40%': 0,
        '41-60%': 0,
        '61-80%': 0,
        '81-100%': 0
    }
    
    # Count resumes in each match score range
    for resume in resumes:
        score = resume.similarity_score
        if score <= 20:
            score_ranges['0-20%'] += 1
        elif score <= 40:
            score_ranges['21-40%'] += 1
        elif score <= 60:
            score_ranges['41-60%'] += 1
        elif score <= 80:
            score_ranges['61-80%'] += 1
        else:
            score_ranges['81-100%'] += 1
    
    return render_template('analytics.html', 
                          job_role_counts=job_role_counts,
                          total_resumes=total_resumes,
                          avg_similarity=avg_similarity,
                          score_ranges=score_ranges)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear session data and database"""
    # Clear session data
    session.clear()
    
    # Clear database tables
    models.Resume.query.delete()
    db.session.commit()
    
    flash('All data has been cleared', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)