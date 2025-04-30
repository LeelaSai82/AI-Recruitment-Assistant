import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Download NLTK data if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    """Preprocess text for NLP analysis"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Join tokens back into string
    return ' '.join(tokens)

def extract_skills_from_job_description(job_description):
    """Extract skills from a job description"""
    # Common technical skills to look for
    common_skills = [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
        'ci/cd', 'agile', 'scrum', 'kanban', 'jira', 'confluence',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'data science', 'machine learning', 'deep learning', 'nlp', 'computer vision',
        'rest api', 'graphql', 'microservices', 'serverless', 'oauth', 'jwt',
        'linux', 'unix', 'bash', 'powershell', 'devops', 'sre', 'security',
        'testing', 'junit', 'selenium', 'cypress', 'jest', 'mocha',
        'aws lambda', 's3', 'ec2', 'rds', 'dynamodb', 'cloudfront', 'route53',
        'azure functions', 'cosmos db', 'blob storage', 'app service', 'azure sql',
        'gcp cloud functions', 'bigquery', 'cloud storage', 'dataflow', 'pub/sub'
    ]
    
    # Preprocess job description
    processed_text = preprocess_text(job_description)
    
    # Extract skills
    extracted_skills = []
    for skill in common_skills:
        # Handle multi-word skills
        skill_pattern = r'\b' + skill.replace('.', '\.').replace('+', '\+') + r'\b'
        if re.search(skill_pattern, processed_text):
            extracted_skills.append(skill)
    
    return extracted_skills

def calculate_similarity(candidate_skills, job_skills):
    """Calculate similarity between candidate skills and job skills"""
    if not candidate_skills or not job_skills:
        return 0.0
    
    # Convert to sets for intersection calculation
    candidate_set = set(candidate_skills)
    job_set = set(job_skills)
    
    # Count matching skills
    matching_skills = candidate_set.intersection(job_set)
    
    # Calculate Jaccard similarity coefficient
    similarity = len(matching_skills) / len(job_set)
    
    # Boost score if critical skills are matched
    if matching_skills:
        similarity = min(similarity * 1.2, 1.0)
    
    return similarity

def compare_documents(doc1, doc2):
    """Compare two documents using TF-IDF and cosine similarity"""
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform the documents
    tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    return cosine_sim[0][0]