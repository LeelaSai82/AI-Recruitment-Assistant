import os
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Gemini API with the provided API key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBDZZJ4NxgNqiQvMHY3JQF2lY-fRZQWCJs")
genai.configure(api_key=API_KEY)

def generate_interview_questions(candidate_name, job_role, skills, job_description, num_questions=5):
    """
    Generate personalized interview questions for a candidate based on their profile and job description
    
    Args:
        candidate_name: Name of the candidate
        job_role: Predicted job role
        skills: List of skills from the candidate's resume
        job_description: Job description text
        num_questions: Number of questions to generate (default: 5)
        
    Returns:
        List of generated interview questions
    """
    try:
        # Create a prompt for Gemini
        prompt = f"""
        You are an expert technical interviewer for {job_role} positions.
        
        Candidate Information:
        - Name: {candidate_name}
        - Job Role: {job_role}
        - Skills: {', '.join(skills)}
        
        Job Description:
        {job_description}
        
        Based on the candidate's skills and the job description, generate {num_questions} highly specific, 
        technical interview questions that will evaluate the candidate's expertise in the required skills. 
        The questions should be challenging but fair, focusing on real-world scenarios.
        
        Please format the response as a list of questions only, without any introductions, 
        numbering, or additional text. Each question should be focused on specific skills 
        from the candidate's profile that match the job requirements.
        """
        
        # Configure the model parameters
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Get a model instance
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config
        )
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Process the response to get clean questions
        raw_questions = response.text.strip().split('\n')
        
        # Clean up the questions (remove numbering and extra whitespace)
        questions = []
        for q in raw_questions:
            # Remove question numbers if present (like "1. ", "Q1: ", etc.)
            cleaned_q = re.sub(r'^(\d+\.|\*|Q\d+:|\-)\s*', '', q.strip())
            if cleaned_q and len(cleaned_q) > 10:  # Ensure it's a valid question
                questions.append(cleaned_q)
        
        # Ensure we have the required number of questions
        while len(questions) < num_questions:
            questions.append(f"Tell me about your experience with {skills[min(len(questions), len(skills)-1)] if skills else job_role}.")
        
        # Limit to the requested number
        return questions[:num_questions]
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        # Return fallback questions if API fails
        return [
            f"Tell me about your experience as a {job_role}.",
            "What is your most challenging project and how did you handle it?",
            "How do you stay updated with the latest developments in your field?",
            "Describe a situation where you had to learn a new technology quickly.",
            "What are your career goals for the next few years?"
        ]

# Fix: Import re module for pattern matching in question cleaning
import re
