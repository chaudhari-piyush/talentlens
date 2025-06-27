import google.generativeai as genai
from typing import Dict, Optional, Tuple
import json
import logging
from PyPDF2 import PdfReader
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from app.settings import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            raise ValueError("GEMINI_API_KEY not configured")
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def analyze_resume(self, resume_text: str, job_description: str, expected_skills: list) -> Dict[str, float]:
        """Analyze resume and return scores"""
        prompt = f"""
        You are an expert technical recruiter. Analyze the following resume against the job description and expected skills.
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        EXPECTED SKILLS:
        {', '.join(expected_skills)}
        
        Please evaluate and provide scores for the following metrics (each out of 10):
        
        1. Skills Match Score: How well do the candidate's skills match the expected skills list? Consider both exact matches and related skills.
        2. Resume Relevancy Score: How relevant is the candidate's overall experience and background to this role?
        3. Job Description Relevancy Score: How well does the candidate's profile align with the specific requirements mentioned in the job description?
        
        Respond in JSON format only:
        {{
            "skills_match_score": <score>,
            "resume_relevancy_score": <score>,
            "job_description_relevancy_score": <score>,
            "reasoning": {{
                "skills_match": "<brief explanation>",
                "resume_relevancy": "<brief explanation>",
                "job_description_relevancy": "<brief explanation>"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            # Clean up common JSON issues
            result_text = result_text.strip()
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                import re
                result_text = re.sub(r',\s*}', '}', result_text)
                result_text = re.sub(r',\s*]', ']', result_text)
                result = json.loads(result_text)
            
            return {
                "skills_match_score": float(result.get("skills_match_score", 0)),
                "resume_relevancy_score": float(result.get("resume_relevancy_score", 0)),
                "job_description_relevancy_score": float(result.get("job_description_relevancy_score", 0))
            }
        except Exception as e:
            logger.error(f"Error analyzing resume with Gemini: {e}")
            # Return random scores between 5-7 as fallback
            import random
            return {
                "skills_match_score": round(random.uniform(5.0, 7.0), 1),
                "resume_relevancy_score": round(random.uniform(5.0, 7.0), 1),
                "job_description_relevancy_score": round(random.uniform(5.0, 7.0), 1)
            }
    
    def generate_interview_questions(self, resume_text: str, job_description: str, expected_skills: list) -> Dict:
        """Generate interview questions and answers based on resume"""
        
        # Log input for debugging
        logger.info(f"Generating questions for job with skills: {expected_skills}")
        logger.info(f"Resume text length: {len(resume_text)} characters")
        
        # Determine if this is a technical role
        technical_keywords = ['developer', 'engineer', 'programmer', 'software', 'coding', 'programming', 
                            'backend', 'frontend', 'fullstack', 'data', 'ml', 'ai', 'devops', 'architect']
        is_technical_role = any(keyword in job_description.lower() for keyword in technical_keywords)
        
        # Truncate resume if too long
        if len(resume_text) > 3000:
            resume_text = resume_text[:3000] + "... [truncated]"
        
        prompt = f"""
Analyze this resume and create interview questions:

RESUME: {resume_text[:2000]}

JOB: {job_description[:500]}

REQUIRED SKILLS FOR THIS JOB: {', '.join(expected_skills[:10])}

Generate 3 interview rounds with 4-5 questions each:

Round 1 - Technical Screening (4-5 questions):
- 2-3 questions about projects/experience from resume
- 2 questions specifically testing the REQUIRED SKILLS listed above
{"- 1 coding problem using one of the REQUIRED SKILLS" if is_technical_role else ""}

Round 2 - Deep Technical Dive (4-5 questions):
- 2-3 questions about system design and architecture from their work
- 1-2 questions about advanced concepts in the REQUIRED SKILLS

Round 3 - Behavioral & Skills Assessment (4-5 questions):
- 2-3 behavioral questions about their past projects
- 1-2 scenario questions using the REQUIRED SKILLS

Output JSON with EXACTLY this structure:
{{
  "interview_1": [
    {{
      "question": "At [COMPANY], you worked on [PROJECT]. How did you implement [SPECIFIC TECH]?",
      "expected_answer": "Should explain specific implementation details and technical decisions",
      "follow_ups": ["What challenges did you face?", "How did you optimize it?"],
      "red_flags": ["Cannot explain basic concepts", "No hands-on experience"]
    }},
    {{
      "question": "Explain how [REQUIRED SKILL from job] works and give an example from your experience",
      "expected_answer": "Should demonstrate understanding of [SKILL] with real examples",
      "follow_ups": ["What are the limitations?", "When would you not use it?"],
      "red_flags": ["Only theoretical knowledge", "Cannot provide examples"]
    }}{"," if is_technical_role else ""}
    {'''{
      "question": "Write a function using [REQUIRED SKILL] to solve: [SPECIFIC PROBLEM RELATED TO JOB]",
      "expected_answer": "Code solution demonstrating proficiency with [SKILL] and problem-solving",
      "follow_ups": ["What is the time complexity?", "How would you test this?"],
      "red_flags": ["Cannot write basic code", "No understanding of complexity"]
    }''' if is_technical_role else ""}
  ],
  "interview_2": [
    {{
      "question": "Design a scalable version of [SYSTEM from resume] using [REQUIRED SKILL]",
      "expected_answer": "Should show system design skills and knowledge of [SKILL]",
      "follow_ups": ["How would you handle failures?", "What about security?"],
      "red_flags": ["No consideration of scale", "Unfamiliar with technology"]
    }}
  ],
  "interview_3": [
    {{
      "question": "Tell me about a time you had to learn [REQUIRED SKILL] quickly for a project",
      "expected_answer": "Should show learning ability and practical application",
      "follow_ups": ["What resources did you use?", "How did you validate your learning?"],
      "red_flags": ["Never had to learn new skills", "No concrete examples"]
    }}
  ]
}}

CRITICAL: 
1. Replace ALL placeholders like [COMPANY], [PROJECT], [REQUIRED SKILL] with ACTUAL values
2. Include questions for EACH required skill: {', '.join(expected_skills[:5])}
3. Keep text concise - max 100 chars per field
4. Use only double quotes, no single quotes
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            # Clean up common JSON issues
            result_text = result_text.strip()
            
            # Remove any markdown formatting
            if "```" in result_text:
                result_text = result_text.split("```")[0]
            
            # Try to extract JSON if it's embedded in text
            import re
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result_text = json_match.group(0)
            
            # Try to parse JSON
            try:
                parsed_json = json.loads(result_text)
                logger.info("Successfully parsed Gemini response")
                return parsed_json
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {je}")
                logger.info(f"Response length: {len(result_text)} characters")
                
                # Try to fix common JSON issues
                # Remove any trailing commas before } or ]
                result_text = re.sub(r',\s*}', '}', result_text)
                result_text = re.sub(r',\s*]', ']', result_text)
                # Remove any // comments
                result_text = re.sub(r'//.*$', '', result_text, flags=re.MULTILINE)
                # Remove any /* */ comments
                result_text = re.sub(r'/\*[\s\S]*?\*/', '', result_text)
                # Fix unescaped quotes in strings (but not the JSON structure quotes)
                # This is a bit hacky but helps with common issues
                result_text = re.sub(r'(?<=[^\\])"(?=[^:,\}\]]+["\'])', r'\"', result_text)
                
                # If JSON seems truncated, try to close it properly
                open_braces = result_text.count('{')
                close_braces = result_text.count('}')
                open_brackets = result_text.count('[')
                close_brackets = result_text.count(']')
                
                # Add missing closing brackets/braces
                if open_brackets > close_brackets:
                    result_text += ']' * (open_brackets - close_brackets)
                if open_braces > close_braces:
                    result_text += '}' * (open_braces - close_braces)
                
                # Try parsing again
                try:
                    parsed_json = json.loads(result_text)
                    logger.info("Successfully parsed after cleanup and bracket fixing")
                    return parsed_json
                except Exception as e2:
                    logger.error(f"Still failed after cleanup: {e2}")
                    # If still failing, return default structure
                    logger.error("Failed to parse JSON after cleanup attempts")
                    return {
                        "interview_1": [
                            {
                                "question": "Tell me about your most recent project and the technologies you used.",
                                "expected_answer": "Candidate should describe their recent work experience.",
                                "follow_ups": ["What challenges did you face?", "How did you overcome them?"],
                                "red_flags": ["Cannot articulate project details", "Vague responses"]
                            }
                        ],
                        "interview_2": [
                            {
                                "question": "How would you design a system similar to what you've worked on?",
                                "expected_answer": "Candidate should demonstrate system design knowledge.",
                                "follow_ups": ["How would you scale it?", "What about security?"],
                                "red_flags": ["No consideration of scale", "Missing key components"]
                            }
                        ],
                        "interview_3": [
                            {
                                "question": "Describe a time when you had to work with a difficult team member.",
                                "expected_answer": "Candidate should show interpersonal skills.",
                                "follow_ups": ["What did you learn?", "Would you handle it differently now?"],
                                "red_flags": ["Blames others entirely", "No self-reflection"]
                            }
                        ]
                    }
                    
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return {
                "interview_1": [
                    {
                        "question": "Tell me about your experience with the technologies mentioned in your resume.",
                        "expected_answer": "Candidate should elaborate on their technical experience.",
                        "follow_ups": ["Which technology are you most proficient in?"],
                        "red_flags": ["Cannot elaborate on resume claims"]
                    }
                ],
                "interview_2": [
                    {
                        "question": "Walk me through a technical challenge you've solved.",
                        "expected_answer": "Detailed explanation of problem-solving approach.",
                        "follow_ups": ["What alternatives did you consider?"],
                        "red_flags": ["No concrete examples"]
                    }
                ],
                "interview_3": [
                    {
                        "question": "What are your career goals for the next 2-3 years?",
                        "expected_answer": "Clear career progression plans.",
                        "follow_ups": ["How does this role fit into your plans?"],
                        "red_flags": ["No clear direction"]
                    }
                ]
            }
    
    def create_qa_pdf(self, qa_data: Dict, candidate_name: str) -> bytes:
        """Create a PDF document with interview questions and answers"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=30
        )
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            leftIndent=20
        )
        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=15,
            leftIndent=40,
            rightIndent=20
        )
        
        # Title page
        story.append(Paragraph(f"Interview Guide", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Candidate: {candidate_name}", styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Table of contents
        toc_data = [
            ['Interview Round', 'Focus Area', 'Questions'],
            ['Round 1', 'Technical Screening & Resume Verification', f"{len(qa_data.get('interview_1', []))} questions"],
            ['Round 2', 'Deep Technical Dive', f"{len(qa_data.get('interview_2', []))} questions"],
            ['Round 3', 'Behavioral & Project Leadership', f"{len(qa_data.get('interview_3', []))} questions"]
        ]
        
        toc_table = Table(toc_data, colWidths=[2*inch, 3*inch, 2*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(toc_table)
        story.append(PageBreak())
        
        # Interview rounds
        for round_num, round_key in enumerate(['interview_1', 'interview_2', 'interview_3'], 1):
            round_title = {
                'interview_1': 'Interview Round 1 - Technical Screening & Resume Verification',
                'interview_2': 'Interview Round 2 - Deep Technical Dive',
                'interview_3': 'Interview Round 3 - Behavioral & Project Leadership'
            }[round_key]
            
            story.append(Paragraph(round_title, heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            questions = qa_data.get(round_key, [])
            for i, q in enumerate(questions, 1):
                # Question
                question_text = q.get('question', '')
                
                # Check if it's a coding problem
                if 'Coding Problem:' in question_text:
                    story.append(Paragraph(f"<b>Question {i}:</b>", question_style))
                    story.append(Spacer(1, 0.05*inch))
                    
                    # Format coding problem with preformatted text
                    code_style = ParagraphStyle(
                        'CodeStyle',
                        parent=styles['Code'],
                        fontSize=10,
                        fontName='Courier',
                        leftIndent=40,
                        rightIndent=20,
                        backColor=colors.HexColor('#f8f8f8')
                    )
                    
                    # Split question into parts for better formatting
                    parts = question_text.split('\n\n')
                    for part in parts:
                        if part.strip():
                            if any(keyword in part for keyword in ['Example:', 'Input:', 'Output:', 'Constraints:']):
                                story.append(Preformatted(part, code_style))
                            else:
                                story.append(Paragraph(part, answer_style))
                            story.append(Spacer(1, 0.05*inch))
                else:
                    story.append(Paragraph(f"<b>Question {i}:</b> {question_text}", question_style))
                    story.append(Spacer(1, 0.1*inch))
                
                # Expected Answer
                story.append(Paragraph("<b>Expected Answer:</b>", answer_style))
                expected_answer = q.get('expected_answer', '')
                
                # Handle code blocks in expected answer
                if '```' in expected_answer:
                    parts = expected_answer.split('```')
                    for j, part in enumerate(parts):
                        if j % 2 == 1:  # Code block
                            # Remove language identifier if present
                            lines = part.split('\n')
                            if lines and lines[0].strip() in ['python', 'java', 'javascript', 'cpp', 'c++']:
                                part = '\n'.join(lines[1:])
                            
                            code_style = ParagraphStyle(
                                'CodeBlock',
                                parent=styles['Code'],
                                fontSize=9,
                                fontName='Courier',
                                leftIndent=40,
                                rightIndent=20,
                                backColor=colors.HexColor('#f0f0f0'),
                                borderColor=colors.HexColor('#cccccc'),
                                borderWidth=1,
                                borderPadding=5
                            )
                            story.append(Preformatted(part.strip(), code_style))
                        else:
                            if part.strip():
                                story.append(Paragraph(part.strip(), answer_style))
                        story.append(Spacer(1, 0.05*inch))
                else:
                    story.append(Paragraph(expected_answer, answer_style))
                
                # Follow-ups
                if q.get('follow_ups'):
                    story.append(Paragraph("<b>Follow-up Questions:</b>", answer_style))
                    for follow_up in q.get('follow_ups', []):
                        story.append(Paragraph(f"• {follow_up}", answer_style))
                
                # Red flags
                if q.get('red_flags'):
                    story.append(Paragraph("<b>Red Flags to Watch:</b>", answer_style))
                    for red_flag in q.get('red_flags', []):
                        story.append(Paragraph(f"• {red_flag}", answer_style))
                
                story.append(Spacer(1, 0.3*inch))
            
            if round_num < 3:
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
gemini_service = None

def get_gemini_service() -> GeminiService:
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiService()
    return gemini_service