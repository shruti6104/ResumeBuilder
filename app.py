# Shrutika's Pro-Level Resume Builder (PDFShift Version)
from flask import Flask, render_template, request, make_response, redirect, url_for
import os
import requests
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
form_data = {}
profile_image_path = ""

PDFSHIFT_API_KEY = "sk_08f5c9c7703b5af1d5efbde8d679ace51ef796ce"  # Replace with your actual PDFShift API key

@app.route('/')
def index():
    return render_template("form.html")

@app.route('/preview', methods=['POST'])
def preview():
    global form_data, profile_image_path
    raw_data = request.form.to_dict()
    form_data = {k: v.strip() for k, v in raw_data.items()}

    if 'profile' in request.files:
        file = request.files['profile']
        if file.filename:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            profile_image_path = path

    return render_template("preview.html", data=form_data, profile_image=profile_image_path)

@app.route('/download')
def download():
    global form_data, profile_image_path
    absolute_path = os.path.abspath(profile_image_path)
    file_url = f"file:///{absolute_path.replace(os.sep, '/')}"
    rendered = render_template("pdf_template.html", data=form_data, profile_image=file_url)

    # Send HTML to PDFShift API
    response = requests.post(
        "https://api.pdfshift.io/v3/convert/html",
        auth=(PDFSHIFT_API_KEY, ''),
        json={"source": rendered}
    )

    if response.status_code == 200:
        pdf = response.content
        res = make_response(pdf)
        res.headers['Content-Type'] = 'application/pdf'
        res.headers['Content-Disposition'] = 'attachment; filename=resume.pdf'
        return res
    else:
        return f"PDF generation failed: {response.text}"

@app.route('/send_email')
def send_email():
    global form_data, profile_image_path
    email = form_data.get("email")
    if not email:
        return "Email address not provided."

    absolute_path = os.path.abspath(profile_image_path)
    file_url = f"file:///{absolute_path.replace(os.sep, '/')}"
    rendered = render_template("pdf_template.html", data=form_data, profile_image=file_url)

    # Convert to PDF using PDFShift
    response = requests.post(
        "https://api.pdfshift.io/v3/convert/html",
        auth=(PDFSHIFT_API_KEY, ''),
        json={"source": rendered}
    )

    if response.status_code != 200:
        return f"PDF generation failed: {response.text}"

    pdf_bytes = response.content

    msg = EmailMessage()
    msg['Subject'] = 'Your Resume from Resume Pro Builder'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = email
    msg.set_content("Hi! Here is your professionally generated resume as a PDF. Best of luck!")

    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename='resume.pdf')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('your_email@gmail.com', 'your_app_password')
            smtp.send_message(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {e}"

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
