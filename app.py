# Shrutika's Pro-Level Resume Builder
from flask import Flask, render_template, request, make_response, redirect, url_for
import pdfkit
import os
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
form_data = {}
profile_image_path = ""

# ✅ Updated path to wkhtmltopdf executable
pdfkit_config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# PDF options to enable access to local files
pdf_options = {
    'enable-local-file-access': None
}

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
    pdf = pdfkit.from_string(rendered, False, configuration=pdfkit_config, options=pdf_options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=resume.pdf'
    return response

@app.route('/send_email')
def send_email():
    global form_data, profile_image_path
    email = form_data.get("email")
    if not email:
        return "Email address not provided."

    absolute_path = os.path.abspath(profile_image_path)
    file_url = f"file:///{absolute_path.replace(os.sep, '/')}"
    rendered = render_template("pdf_template.html", data=form_data, profile_image=file_url)
    pdf_bytes = pdfkit.from_string(rendered, False, configuration=pdfkit_config, options=pdf_options)

    msg = EmailMessage()
    msg['Subject'] = 'Your Resume from Resume Pro Builder'
    msg['From'] = 'svd0651@gmail.com'
    msg['To'] = email
    msg.set_content("Hi! Here is your professionally generated resume as a PDF. Best of luck!")

    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename='resume.pdf')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('svd0651@gmail.com', 'omrf hqjr tumu kjmo')
            smtp.send_message(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {e}"

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
