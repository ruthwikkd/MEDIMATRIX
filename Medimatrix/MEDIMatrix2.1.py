import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import cv2
import smtplib
from fpdf import FPDF
import random
import string
import os

# Load your dataset (replace 'Testing.csv' with your dataset)
data = pd.read_csv('Testing.csv')

# Check if the dataset contains a column for the diagnosis
if 'prognosis' not in data.columns:
    print("The dataset does not contain a 'prognosis' column. Please check the column name.")
else:
    # Encode the labels (disease names)
    label_encoder = LabelEncoder()
    data['prognosis'] = label_encoder.fit_transform(data['prognosis'])

    # Split the data into features and labels
    symptoms = data.columns[:-1]
    X = data[symptoms]
    y = data['prognosis']

    # Create and train a decision tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X, y)

# Define a function to generate a random ID
def generate_random_id():
    letters = string.ascii_letters
    digits = string.digits
    random_id = ''.join(random.choice(letters) for _ in range(5))
    random_id += ''.join(random.choice(digits) for _ in range(5))
    return random_id

# Define a function to save the prediction report as a PDF with a centered watermark
def save_report_as_pdf(user_name, user_age, user_phone, selected_symptoms, predicted_disease):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Generate a random ID
    random_id = generate_random_id()
    
    # Load the watermark image
    watermark = Image.open("wlc.jpg")
    page_width = pdf.w
    page_height = pdf.h

    corner_x = 80  # Adjust this value as needed to control the X position (20 units from the left edge)
    corner_y = 20  # Adjust this value as needed to control the Y position (20 units from the top edge)

    # Define the size of the watermark
    watermark_width = 1.5 * 42 # 2.5 inches converted to points (1 inch = 72 points)
    watermark_height = 1.5 * 42

    # Place the watermark on the PDF page in the corner
    pdf.image("wlc.jpg", x=corner_x, y=corner_y, w=watermark_width, h=watermark_height)

    pdf.cell(200, 10, txt=f"ID: {random_id}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Patient Name: {user_name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Patient Age: {user_age}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Phone Number: {user_phone}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Selected Symptoms:", ln=True, align='L')
    for symptom in selected_symptoms:
        pdf.cell(200, 10, txt=f" - {symptom}", ln=True, align='L')
    pdf.multi_cell(0, 10, f"Predicted Disease: {predicted_disease}", align='L')

    pdf.multi_cell(0, 10, f"Health Suggestions: Your health is important. It is recommended to consult a healthcare professional for a detailed evaluation and follow their advice.", align='L')

    pdf.multi_cell(0, 10, f"We also want to highlight the benefits of incorporating Ayurvedic Indian home supplies into your daily routine. Ayurveda, the ancient Indian system of medicine, emphasizes the use of natural remedies and lifestyle practices to promote holistic well-being.")

    pdf.multi_cell(0, 10, f"Ayurvedic remedies often include herbs, spices, and other natural ingredients that are known for their health-promoting properties. For example, turmeric, a common spice in Indian cuisine, is renowned for its anti-inflammatory and antioxidant properties.")

    pdf.multi_cell(0, 10, f"Similarly, black pepper is not just a spice but also has potential health benefits. It may aid digestion and enhance nutrient absorption, contributing to overall well-being.")

    pdf.multi_cell(0, 10, f"Explore the diverse range of Indian medicinal elements like neem, ginger, and holy basil, each known for its unique health benefits. Including these in your diet may provide additional support for your well-being.")

    pdf.multi_cell(0, 10, f"Additionally, Ayurveda recognizes the importance of individualized health plans based on your unique constitution (dosha). If you are interested in exploring Ayurvedic approaches further, you may consult with an Ayurvedic practitioner for personalized guidance.")

    pdf.multi_cell(0, 10, f"Thank you, {user_name}, for visiting Medi Matrix. We wish you good health and success on your journey to well-being, whether through traditional medical advice or holistic approaches like Ayurveda.", align='L')

    
    pdf_file_name = f"{user_name}_report.pdf"
    pdf.output(pdf_file_name)
    return pdf_file_name

# Define a function to send the prediction report via email
def email_report(user_name, user_age, user_phone, selected_symptoms, predicted_disease, user_email):
    sender_email = "projectshubofrknani@gmail.com"  # Replace with your email
    sender_password = "xpgq dkbt qgvk kjqi"  # Replace with your password

    message = f"Subject: Medical Repor\nPatient Name: {user_name}\nPatient Age: {user_age}\nPhone Number: {user_phone}\nEmail: {user_email}\n\nSelected Symptoms:\n"
    message += "\n".join(f" - {symptom}" for symptom in selected_symptoms)
    message += f"\n\nHealth Suggestions: Your health is important. It is recommended to consult a healthcare professional for a detailed evaluation and follow their advice."
    message += f"\n\nThank you, {user_name}, for visiting Medi Matrix. We wish you good health."
    message +=f"\n\n\n This project is under testing AND IMPROVEMENT:- and this this projevct is made by:-\nD.RUTHWIKK-E22CSEU0230\nCH.TRILOKESH-E22CSEU0221\nK.MADHAVAN-E22CSEU0240\nN.SUBODH-E22CSEU0225"


    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        pdf_file_name = save_report_as_pdf(user_name, user_age, user_phone, selected_symptoms, predicted_disease)
        pdf_file = open(pdf_file_name, 'rb')

        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "Medical Report"

        body = message
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF report
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_file.close()
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_file_name)
        msg.attach(pdf_attachment)

        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        messagebox.showinfo("Email Report", "Report has been sent via email.")
        
        # Delete the temporary PDF file after sending it
        os.remove(pdf_file_name)

    except Exception as e:
        messagebox.showerror("Email Report Error", f"An error occurred: {str(e)}")
def clear_page():
    for widget in main_window.winfo_children():
        widget.destroy()

# Create a function to display the symptoms selection page
def show_symptoms_page(user_name, user_age, user_phone):
    clear_page()  # Clear the current page

    # Create a new page for selecting symptoms
    symptoms_page = tk.Toplevel()
    symptoms_page.title(f"Welcome {user_name} to Medi Matrix")

    # Create a canvas for the symptoms list with a scrollbar
    canvas = tk.Canvas(symptoms_page)
    canvas.pack(side='left', fill='both', expand=True)
    scrollbar = ttk.Scrollbar(symptoms_page, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')
    canvas.configure(yscrollcommand=scrollbar.set)

    symptoms_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=symptoms_frame, anchor='nw')

    tk.Label(symptoms_frame, text="Select symptoms that you are trying to get predicted:").pack()

    selected_symptoms = []

    def add_symptom(symptom):
        selected_symptoms.append(symptom)

    for i, symptom in enumerate(symptoms):
        ttk.Checkbutton(symptoms_frame, text=symptom, command=lambda s=symptom: add_symptom(s)).pack(anchor='w')

    def predict_disease():
        # Prepare the user's input data for prediction
        user_input = pd.DataFrame(columns=symptoms)
        user_input.loc[0] = [1 if symptom in selected_symptoms else 0 for symptom in symptoms]

        # Predict the disease using the decision tree model
        predicted_disease = label_encoder.inverse_transform(clf.predict(user_input))[0]

        result_page = tk.Toplevel()
        result_page.title("Prediction Result")

        result_label = tk.Label(result_page, text=f"Welcome {user_name}!\nPredicted Disease: {predicted_disease}")
        result_label.pack()

        def collect_email_and_send_report():
            email_window = tk.Toplevel(result_page)
            email_window.title("Email Collection")
            email_label = tk.Label(email_window, text="Enter your email address:")
            email_label.pack()
            email_entry = tk.Entry(email_window)
            email_entry.pack()

            def send_report():
                user_email = email_entry.get()
                if not user_email:
                    messagebox.showerror("Email Error", "Please enter your email address.")
                else:
                    email_window.destroy()
                    email_report(user_name, user_age, user_phone, selected_symptoms, predicted_disease, user_email)

            email_button = ttk.Button(email_window, text="Send Report via Email", command=send_report)
            email_button.pack()

        send_email_button = ttk.Button(result_page, text="Email Report", command=collect_email_and_send_report)
        send_email_button.pack()

        save_pdf_button = ttk.Button(result_page, text="Save Report as PDF", command=lambda: save_report_as_pdf(user_name, user_age, user_phone, selected_symptoms, predicted_disease))
        save_pdf_button.pack()

        exit_button = ttk.Button(result_page, text="Exit", command=result_page.destroy)
        exit_button.pack()

    ttk.Button(symptoms_frame, text="Predict Disease", command=predict_disease).pack()

    # Configure the canvas to scroll
    symptoms_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Create a function to display the user input form
def show_form():
    intro_button.pack_forget()  # Hide the "Intro" button
    clear_page()  # Clear the page

    name_label = ttk.Label(main_window, text="Name:")
    name_label.pack()
    name_entry = ttk.Entry(main_window)
    name_entry.pack()

    age_label = ttk.Label(main_window, text="Age:")
    age_label.pack()
    age_entry = ttk.Entry(main_window)
    age_entry.pack()

    phone_label = ttk.Label(main_window, text="Phone Number (10 digits):")
    phone_label.pack()
    phone_entry = ttk.Entry(main_window)
    phone_entry.pack()

    def show_symptoms():
        user_name = name_entry.get()
        user_age = age_entry.get()
        user_phone = phone_entry.get()
        if not user_name:
            messagebox.showerror("Name Error", "Please enter your name.")
        elif not user_age:
            messagebox.showerror("Age Error", "Please enter your age.")
        elif not user_phone or not user_phone.isdigit() or len(user_phone) != 10:
            messagebox.showerror("Phone Number Error", "Please enter a valid 10-digit phone number.")
        else:
            show_symptoms_page(user_name, user_age, user_phone)

    next_button = ttk.Button(main_window, text="Next", command=show_symptoms)
    next_button.pack()

    exit_button = ttk.Button(main_window, text="Exit", command=main_window.destroy)
    exit_button.pack()

# Create a function to display the introduction video
def play_intro_video():
    intro_button.pack_forget()  # Hide the "Intro" button
    cap = cv2.VideoCapture('intro.mp4')  # Replace 'intro.mp4' with your video file
    if not cap:
        messagebox.showerror("Video Error", "Failed to open the video.")
        return

    # Create a window for video playback
    intro_window = tk.Toplevel()
    intro_window.title("Intro Video")

    video_label = tk.Label(intro_window)
    video_label.pack()

    def update_frame():
        ret, frame = cap.read()
        if not ret:
            cap.release()
            intro_window.withdraw()  # Hide the video window
            intro_button.pack()  # Show the "Intro" button again
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (400, 300))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        video_label.config(image=photo)
        video_label.image = photo
        intro_window.after(20, update_frame)

    update_frame()

# Create the main window
main_window = tk.Tk()
main_window.title("Disease Prediction System")
main_window.geometry("400x400")  # Set the window size

# Load and display the welcome image
welcome_image = Image.open("wlc.jpg")
welcome_image = welcome_image.resize((400, 300))
welcome_photo = ImageTk.PhotoImage(welcome_image)
welcome_label = ttk.Label(main_window, image=welcome_photo)
welcome_label.pack()

# Create the "Intro" button
intro_button = ttk.Button(main_window, text="Intro", command=play_intro_video)
intro_button.pack()

# Add "Next" button to the main window
next_button = ttk.Button(main_window, text="Next", command=show_form)
next_button.pack()

# Add "Exit" button to the main window
exit_button = ttk.Button(main_window, text="Exit", command=main_window.destroy)
exit_button.pack()

# Center the content in the middle of the window
main_window.update_idletasks()
main_window.geometry("400x400+" + str((main_window.winfo_screenwidth() - 400) // 2) + "+" + str((main_window.winfo_screenheight() - 400) // 2))

# Start the GUI application
main_window.mainloop()
