import os
import re
import PyPDF2
import docx2txt
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK data if needed
nltk.download('punkt')
nltk.download('stopwords')

def read_pdf(file_path):
    """Extract text content from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def read_docx(file_path):
    """Extract text content from DOCX file"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def read_txt(file_path):
    """Read text content from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def extract_text_from_file(file_path):
    """Extract text from a file based on its extension"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return read_pdf(file_path)
    elif file_extension == '.docx':
        return read_docx(file_path)
    elif file_extension == '.txt':
        return read_txt(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return ""

def preprocess_text(text):
    """Clean and preprocess the text"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_skills_from_resume(file_path):
    """Extract relevant skills from a resume"""
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
        'gcp cloud functions', 'bigquery', 'cloud storage', 'dataflow', 'pub/sub',
        'go', 'golang', 'rust', 'scala', 'typescript', 'php', 'r', 'matlab',
        'hadoop', 'spark', 'kafka', 'airflow', 'databricks', 'tableau', 'power bi',
        'websocket', 'socket.io', 'redux', 'mobx', 'vuex', 'pinia', 'next.js', 'nuxt.js',
        'jquery', 'webpack', 'babel', 'vite', 'rollup', 'sass', 'scss', 'less',
        'responsive design', 'pwa', 'web components', 'webassembly', 'web3', 'blockchain',
        'graphdb', 'neo4j', 'etl', 'data warehouse', 'data lake', 'data engineering'
    ]
    
    # Extract text from file
    text = extract_text_from_file(file_path)
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Extract skills
    extracted_skills = []
    for skill in common_skills:
        # Handle multi-word skills by creating proper regex pattern
        # Replace special regex characters in the skill name
        skill_pattern = r'\b' + skill.replace('.', '\.').replace('+', '\+') + r'\b'
        if re.search(skill_pattern, processed_text):
            extracted_skills.append(skill)
    
    return extracted_skills

def predict_job_role(skills):
    """Predict the most likely job role based on skills"""
    # Define skill sets for different job roles
    role_skills = {
        'Frontend Developer': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'redux', 'sass', 'less', 'bootstrap', 'tailwind', 'typescript', 'jquery', 'webpack', 'babel'],
        'Backend Developer': ['python', 'java', 'node.js', 'express', 'django', 'flask', 'spring', 'php', 'ruby', 'golang', 'rest api', 'graphql', 'microservices', 'sql', 'mongodb'],
        'Full Stack Developer': ['html', 'css', 'javascript', 'react', 'python', 'node.js', 'express', 'django', 'sql', 'mongodb', 'rest api', 'docker'],
        'DevOps Engineer': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'aws', 'azure', 'gcp', 'linux', 'bash', 'terraform', 'ansible', 'git', 'monitoring'],
        'Data Scientist': ['python', 'r', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'data science', 'machine learning', 'deep learning', 'sql', 'statistics'],
        'Data Engineer': ['python', 'sql', 'hadoop', 'spark', 'kafka', 'airflow', 'etl', 'data warehouse', 'mongodb', 'postgresql', 'aws', 'azure'],
        'Cloud Engineer': ['aws', 'azure', 'gcp', 'terraform', 'cloudformation', 'kubernetes', 'docker', 'ci/cd', 'linux', 'networking', 'security'],
        'Security Engineer': ['security', 'penetration testing', 'oauth', 'jwt', 'encryption', 'firewall', 'linux', 'networking', 'python', 'compliance'],
        'Mobile Developer': ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'mobile', 'java', 'objective-c'],
        'QA Engineer': ['testing', 'junit', 'selenium', 'cypress', 'jest', 'mocha', 'test automation', 'manual testing', 'quality assurance', 'ci/cd']
    }
    
    # Count matching skills for each role
    role_matches = {}
    for role, role_skill_list in role_skills.items():
        matches = set(skills).intersection(set(role_skill_list))
        role_matches[role] = len(matches)
    
    # Find role with most matching skills
    best_role = max(role_matches.items(), key=lambda x: x[1])[0]
    
    # If no clear match, return a default role
    if role_matches[best_role] == 0:
        return "Software Developer"
    
    return best_role