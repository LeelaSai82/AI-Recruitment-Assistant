import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import uuid
import json

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize database
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "recruitment_assistant_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - using SQLite for local development
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///recruitment.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the app with SQLAlchemy
db.init_app(app)

# Import resume parser and other utilities
from utils.resume_parser import extract_skills_from_resume, predict_job_role
from utils.nlp_utils import calculate_similarity, extract_skills_from_job_description
from utils.gemini_utils import generate_interview_questions

# Import models
with app.app_context():
    import models
    db.create_all()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    """Home page with resume upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resumes():
    """Handle resume uploads"""
    if 'resumes' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    files = request.files.getlist('resumes')
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        flash('Job description is required', 'danger')
        return redirect(request.url)
    
    # Store job description in session
    session['job_description'] = job_description
    
    # Extract skills from job description
    job_skills = extract_skills_from_job_description(job_description)
    session['job_skills'] = job_skills

    # Process each uploaded resume
    parsed_resumes = []
    job_role_counts = {}

    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            try:
                # Extract candidate information from resume
                candidate_name = filename.split('.')[0]  # Using filename as candidate name
                candidate_skills = extract_skills_from_resume(filepath)
                job_role = predict_job_role(candidate_skills)
                similarity_score = calculate_similarity(candidate_skills, job_skills)
                
                # Update job role counts for analytics
                if job_role in job_role_counts:
                    job_role_counts[job_role] += 1
                else:
                    job_role_counts[job_role] = 1
                
                # Store resume data
                new_resume = models.Resume(
                    filename=filename,
                    filepath=filepath,
                    candidate_name=candidate_name,
                    job_role=job_role,
                    skills=json.dumps(candidate_skills),
                    similarity_score=similarity_score
                )
                db.session.add(new_resume)
                
                # Add to parsed resumes list
                parsed_resumes.append({
                    'id': new_resume.id,
                    'candidate_name': candidate_name,
                    'job_role': job_role,
                    'skills': candidate_skills,
                    'similarity_score': similarity_score
                })
                
            except Exception as e:
                app.logger.error(f"Error processing {filename}: {str(e)}")
                flash(f"Error processing {filename}: {str(e)}", 'danger')
    
    # Save all data to database
    db.session.commit()
    
    # Store job role counts in session for analytics
    session['job_role_counts'] = job_role_counts
    
    # Sort resumes by similarity score
    parsed_resumes.sort(key=lambda x: x['similarity_score'], reverse=True)
    session['parsed_resumes'] = parsed_resumes
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    """Show matching results page"""
    parsed_resumes = session.get('parsed_resumes', [])
    job_description = session.get('job_description', '')
    job_skills = session.get('job_skills', [])
    
    if not parsed_resumes:
        flash('No resumes processed. Please upload resumes first.', 'warning')
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                          resumes=parsed_resumes, 
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
    avg_similarity = sum([r.similarity_score for r in resumes]) / len(resumes) if resumes else 0
    
    return render_template('analytics.html', 
                          job_role_counts=job_role_counts,
                          total_resumes=total_resumes,
                          avg_similarity=avg_similarity)

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
