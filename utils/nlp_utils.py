import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Ensure we're using the correct tokenizers
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    # We'll modify our tokenization approach to avoid punkt_tab
    pass

# List of common skills
SKILLS = [
    'python', 'java', 'javascript', 'js', 'html', 'css', 'react', 'angular', 'vue', 'node', 'express',
    'django', 'flask', 'fastapi', 'php', 'laravel', 'ruby', 'rails', 'golang', 'go', 'rust', 'c++', 'c#',
    'typescript', 'swift', 'kotlin', 'objective-c', 'scala', 'perl', 'r', 'matlab', 'sql', 'nosql',
    'mongodb', 'mysql', 'postgresql', 'oracle', 'cassandra', 'redis', 'aws', 'azure', 'gcp', 'docker',
    'kubernetes', 'jenkins', 'git', 'jira', 'confluence', 'bitbucket', 'gitlab', 'github',
    'ci/cd', 'agile', 'scrum', 'kanban', 'rest', 'graphql', 'soap', 'microservices', 'serverless',
    'elasticsearch', 'kibana', 'logstash', 'splunk', 'prometheus', 'grafana', 'tensorflow', 'pytorch',
    'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi',
    'hadoop', 'spark', 'kafka', 'airflow', 'linux', 'unix', 'bash', 'shell', 'powershell', 'ansible',
    'terraform', 'puppet', 'chef', 'swagger', 'postman', 'webservices', 'api', 'mvc', 'mvvm',
    'bootstrap', 'sass', 'less', 'webpack', 'babel', 'jquery', 'redux', 'vuex', 'webpack', 'npm',
    'yarn', 'oauth', 'jwt', 'saml', 'ldap', 'active directory', 'sso', 'machine learning', 'deep learning',
    'nlp', 'computer vision', 'ai', 'data science', 'data analysis', 'data mining', 'etl', 'web development',
    'frontend', 'backend', 'full stack', 'mobile development', 'android', 'ios', 'cross-platform',
    'xamarin', 'react native', 'flutter', 'ionic', 'cordova', 'devops', 'sre', 'security', 'penetration testing',
    'ethical hacking', 'cloud computing', 'big data', 'blockchain', 'cryptocurrency', 'iot', 'crm', 'erp',
    'sap', 'salesforce', 'dynamics', 'test automation', 'selenium', 'cypress', 'jest', 'mocha', 'chai',
    'jasmine', 'karma', 'junit', 'pytest', 'cucumber', 'bdd', 'tdd', 'agile', 'scrum', 'product management',
]

def preprocess_text(text):
    """Preprocess text for NLP analysis"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Simple tokenization - split by whitespace
    # This avoids the need for punkt_tab
    tokens = text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def extract_skills_from_job_description(job_description):
    """Extract skills from a job description"""
    if not job_description:
        return []
    
    # Preprocess job description
    preprocessed_text = preprocess_text(job_description)
    
    # Extract skills by matching words and phrases
    detected_skills = []
    
    for skill in SKILLS:
        # Look for the skill as a whole word
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, preprocessed_text):
            detected_skills.append(skill)
    
    return list(set(detected_skills))  # Remove duplicates

def calculate_similarity(candidate_skills, job_skills):
    """Calculate similarity between candidate skills and job skills"""
    if not candidate_skills or not job_skills:
        return 0.0
    
    # Create sets of skills for easier operations
    candidate_set = set(candidate_skills)
    job_set = set(job_skills)
    
    # Find matches
    matching_skills = candidate_set.intersection(job_set)
    
    # Calculate Jaccard similarity: |A ∩ B| / |A ∪ B|
    union_skills = candidate_set.union(job_set)
    
    if not union_skills:
        return 0.0
    
    jaccard_similarity = len(matching_skills) / len(union_skills)
    
    # Calculate overlap coefficient: |A ∩ B| / min(|A|, |B|)
    min_size = min(len(candidate_set), len(job_set))
    
    if min_size == 0:
        return 0.0
    
    overlap_coefficient = len(matching_skills) / min_size
    
    # Weighted average of both similarity metrics
    # Giving more weight to overlap coefficient as it's more relevant for matching
    similarity_score = (0.3 * jaccard_similarity) + (0.7 * overlap_coefficient)
    
    return round(similarity_score * 100, 2)  # Return as percentage

def compare_documents(doc1, doc2):
    """Compare two documents using TF-IDF and cosine similarity"""
    if not doc1 or not doc2:
        return 0.0
    
    # Preprocess documents
    preprocessed_doc1 = preprocess_text(doc1)
    preprocessed_doc2 = preprocess_text(doc2)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([preprocessed_doc1, preprocessed_doc2])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return round(similarity * 100, 2)  # Return as percentage
