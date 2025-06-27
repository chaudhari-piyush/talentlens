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
            
            result = json.loads(result_text)
            
            return {
                "skills_match_score": float(result.get("skills_match_score", 0)),
                "resume_relevancy_score": float(result.get("resume_relevancy_score", 0)),
                "job_description_relevancy_score": float(result.get("job_description_relevancy_score", 0))
            }
        except Exception as e:
            logger.error(f"Error analyzing resume with Gemini: {e}")
            return {
                "skills_match_score": 0.0,
                "resume_relevancy_score": 0.0,
                "job_description_relevancy_score": 0.0
            }
    
    def generate_interview_questions(self, resume_text: str, job_description: str, expected_skills: list) -> Dict:
        """Generate interview questions and answers based on resume"""
        
        # Determine if this is a technical role
        technical_keywords = ['developer', 'engineer', 'programmer', 'software', 'coding', 'programming', 
                            'backend', 'frontend', 'fullstack', 'data', 'ml', 'ai', 'devops', 'architect']
        is_technical_role = any(keyword in job_description.lower() for keyword in technical_keywords)
        
        prompt = f"""
        You are an expert technical interviewer preparing highly specific, personalized interview questions based on the candidate's actual experience and the job requirements.
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        EXPECTED SKILLS:
        {', '.join(expected_skills)}
        
        CRITICAL INSTRUCTIONS:
        1. Questions MUST be HIGHLY SPECIFIC to the candidate's resume. Reference their actual projects, companies, technologies, and experiences.
        2. Avoid generic questions. Every question should be impossible to ask without reading their resume.
        3. For technical roles, include actual coding problems relevant to their experience.
        4. Expected answers should be based on what this specific candidate should know given their background.
        
        Generate interview questions divided into three rounds:
        
        1. **Interview Round 1 - Technical Screening & Resume Verification** (6-7 questions):
           - Ask about SPECIFIC projects mentioned in their resume
           - Verify technologies they claim to have used with detailed questions
           - Ask them to explain specific technical decisions from their past work
           {"- Include 1 MEDIUM difficulty coding problem relevant to their experience and the job requirements" if is_technical_role else ""}
           - Questions like "In your project at [Company X], you mentioned using [Technology Y]. What specific challenges did you face?"
        
        2. **Interview Round 2 - Deep Technical Dive** (5-6 questions):
           - Deep dive into their most relevant project
           - System design questions based on systems they've actually worked on
           - Ask them to extend or improve something they built
           - Questions like "How would you scale the [specific system] you built at [Company]?"
           - Technology-specific questions based on their tech stack
        
        3. **Interview Round 3 - Behavioral & Project Leadership** (5-6 questions):
           - Ask about specific team situations from their resume
           - Challenges they faced in mentioned projects
           - Questions about specific achievements or metrics they mentioned
           - Their role in specific projects and decision-making process
        
        For each question, provide:
        - The question itself (MUST reference specific details from their resume)
        - Expected answer points (based on their specific experience)
        - Follow-up questions to probe deeper into their actual work
        - Red flags to watch for
        
        {"For coding problems, use multiline strings in the question and expected_answer fields." if is_technical_role else ""}
        
        Respond in JSON format:
        {{
            "interview_1": [
                {{
                    "question": "<question>",
                    "expected_answer": "<detailed expected answer>",
                    "follow_ups": ["<follow-up 1>", "<follow-up 2>"],
                    "red_flags": ["<red flag 1>", "<red flag 2>"]
                }}
            ],
            "interview_2": [...],
            "interview_3": [...]
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
            
            return json.loads(result_text)
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return {
                "interview_1": [],
                "interview_2": [],
                "interview_3": []
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