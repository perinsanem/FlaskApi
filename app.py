from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import spacy
import base64
import io

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_content):
    text = ""
    reader = PdfReader(pdf_content)
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    return keywords

def score_cv(keywords, cv_text):
    keyword_count = sum(1 for keyword in keywords if keyword in cv_text.lower())
    score = keyword_count / len(keywords) * 100  
    return score

@app.route('/process-job-data', methods=['POST'])
def process_job_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        job_keywords = data.get('job_keywords')
        resumes = data.get('resumes')

        if not job_keywords or not isinstance(job_keywords, str):
            return jsonify({'error': 'Invalid or missing job keywords'}), 400

        if not resumes or not isinstance(resumes, list):
            return jsonify({'error': 'Invalid or missing resumes'}), 400

        extracted_keywords = extract_keywords(job_keywords)
        
        scores_with_ids = []
        for idx, resume_base64 in enumerate(resumes, start=1):
            resume_bytes = base64.b64decode(resume_base64)
            cv_text = extract_text_from_pdf(io.BytesIO(resume_bytes))
            cv_score = "{:.2f}".format(score_cv(extracted_keywords, cv_text))
            scores_with_ids.append({'id': idx, 'score': cv_score})
            app.logger.info(f"PDF ID: {idx}, CV Score: {cv_score}")

        return jsonify({'job_keywords': job_keywords, 'scores': scores_with_ids}), 200

    except Exception as e:
        app.logger.error(f"Error processing job data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
