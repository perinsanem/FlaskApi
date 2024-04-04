from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process-job-data', methods=['POST'])
def process_job_data():
    data = request.get_json()

    

    job_keywords = data.get('job_keywords')
    resumes = data.get('resumes')

    print("Job keywords:", job_keywords)
  
   

   
    return jsonify({'job_keywords': job_keywords, 'resumes': resumes})

if __name__ == '__main__':
    app.run(debug=True)
