import os
import re
import logging
from PyPDF2 import PdfReader
import docx2txt
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Lists of skills and job roles for matching
TECH_SKILLS = [
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

JOB_ROLES = {
    'web developer': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'node', 'express', 'frontend', 'backend', 'jquery', 'bootstrap'],
    'data scientist': ['python', 'r', 'machine learning', 'deep learning', 'statistics', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'data analysis'],
    'software engineer': ['java', 'c++', 'c#', 'algorithms', 'data structures', 'object-oriented', 'design patterns', 'api'],
    'devops engineer': ['docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'terraform', 'ansible', 'ci/cd'],
    'data engineer': ['sql', 'etl', 'hadoop', 'spark', 'kafka', 'data warehouse', 'data lake', 'airflow'],
    'mobile developer': ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'mobile'],
    'ux/ui designer': ['ux', 'ui', 'user interface', 'user experience', 'figma', 'sketch', 'adobe xd', 'wireframes'],
    'security engineer': ['security', 'penetration testing', 'vulnerability assessment', 'cryptography', 'siem'],
    'product manager': ['product', 'roadmap', 'agile', 'scrum', 'user stories', 'stakeholder', 'requirements'],
    'qa engineer': ['testing', 'selenium', 'test automation', 'quality assurance', 'cypress', 'junit', 'pytest']
}

def read_pdf(file_path):
    """Extract text content from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {str(e)}")
        return ""

def read_docx(file_path):
    """Extract text content from DOCX file"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        logger.error(f"Error reading DOCX file {file_path}: {str(e)}")
        return ""

def read_txt(file_path):
    """Read text content from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading TXT file {file_path}: {str(e)}")
        return ""

def extract_text_from_file(file_path):
    """Extract text from a file based on its extension"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.txt':
        return read_txt(file_path)
    else:
        logger.error(f"Unsupported file format: {ext}")
        return ""

def preprocess_text(text):
    """Clean and preprocess the text"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters, keeping alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    return tokens

def extract_skills_from_resume(file_path):
    """Extract relevant skills from a resume"""
    # Read text from file
    text = extract_text_from_file(file_path)
    if not text:
        return []
    
    # Preprocess the text
    tokens = preprocess_text(text)
    
    # Create n-grams for multi-word skills
    unigrams = tokens
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]
    trigrams = [f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}" for i in range(len(tokens)-2)]
    
    # Combine all n-grams
    all_grams = unigrams + bigrams + trigrams
    
    # Extract skills from text
    detected_skills = []
    
    for skill in TECH_SKILLS:
        if skill in all_grams or any(skill in gram for gram in all_grams):
            detected_skills.append(skill)
    
    return list(set(detected_skills))  # Remove duplicates

def predict_job_role(skills):
    """Predict the most likely job role based on skills"""
    if not skills:
        return "Unknown"
    
    role_scores = {}
    
    for role, role_skills in JOB_ROLES.items():
        # Calculate the number of matching skills
        matching_skills = [skill for skill in skills if skill in role_skills]
        score = len(matching_skills) / len(role_skills) if role_skills else 0
        role_scores[role] = score
    
    # Get the role with the highest score
    if role_scores:
        max_role = max(role_scores.items(), key=lambda x: x[1])
        # Only return a role if the score is above a threshold
        if max_role[1] > 0.1:
            return max_role[0].title()
    
    return "General IT Professional"
