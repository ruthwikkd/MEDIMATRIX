import tkinter as tk
from tkinter import messagebox, Listbox
from PIL import Image, ImageTk
import cv2
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from reportlab.pdfgen import canvas
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from tkinter import simpledialog
from fpdf import FPDF

df = pd.read_csv('Training.csv')

# Assuming 'prognosis' is the column with disease labels
X = df.drop('prognosis', axis=1)
y = df['prognosis']

# Initialize the Decision Tree classifier
model = DecisionTreeClassifier()
model.fit(X, y)

class GUIPage:
    def __init__(self, root, background_image_path, welcome_image_path, intro_video_path):
        self.root = root
        self.root.title("GUI with Background Image")

        background_image = Image.open(background_image_path)
        self.background_image = ImageTk.PhotoImage(background_image)

        welcome_image = Image.open(welcome_image_path)
        self.welcome_image = ImageTk.PhotoImage(welcome_image)

        image_width, image_height = background_image.size

        # Get the screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the center coordinates for the initial window
        center_x = int((screen_width - 800) / 2)
        center_y = int((screen_height - 500) / 2)

        self.root.geometry(f"800x500+{center_x}+{center_y}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=image_width, height=image_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        button_font = ("Cavolini", 12, "bold")

        self.intro_button = tk.Button(root, text="Intro", command=self.play_intro, bg="blue", fg="white", font=button_font)
        self.intro_button.place(x=625, y=290)

        self.next_button = tk.Button(root, text="Next", command=self.show_next, bg="green", fg="white", font=button_font)
        self.next_button.place(x=625, y=350)

        self.exit_button = tk.Button(root, text="Exit", command=self.root.destroy, bg="red", fg="white", font=button_font)
        self.exit_button.place(x=625, y=410)

        self.welcome_image_label = tk.Label(root, image=self.welcome_image)
        self.welcome_image_label.place(x=550, y=10)

        self.intro_video_path = intro_video_path
        self.cap = None

        # Variables to store user details
        self.user_name = tk.StringVar()
        self.user_age = tk.StringVar()
        self.user_phone = tk.StringVar()

        # Flag to check if user details are submitted
        self.details_submitted = False

        # Additional variables for symptoms and prediction
        self.selected_symptoms = []
        self.predicted_disease = ""

    def play_intro(self):
        self.intro_button.place_forget()
        self.cap = cv2.VideoCapture(self.intro_video_path)

        if not self.cap.isOpened():
            messagebox.showerror("Video Error", "Failed to open the video.")
            self.intro_button.place(x=625, y=290)
            return

        intro_window = tk.Toplevel()
        intro_window.title("Intro Video")

        video_label = tk.Label(intro_window)
        video_label.pack()

        def update_frame():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                intro_window.withdraw()
                self.intro_button.place(x=625, y=290)
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            video_label.config(image=photo)
            video_label.image = photo
            intro_window.after(20, update_frame)

        update_frame()

    def show_next(self):
        # Clear the canvas and remove all buttons
        self.canvas.delete("all")
        self.intro_button.destroy()
        self.next_button.destroy()
        self.exit_button.destroy()
        welcome_label = tk.Label(self.root, text="Welcome to MEDIMATRIX (SET SCALE)", font=("Cavolini", 20, "bold"))
        welcome_label.pack(pady=80)
        self.prompt_user_details()

    def prompt_user_details(self):
        welcome_label = tk.Label(self.root, text="Welcome to MEDIMATRIX ", font=("Rastanty Cortez", 20, "bold"))
        welcome_label.place(x=100, y=100)
        prediction_label = tk.Label(self.root, text="DISEASE PREDICTION BASED ON SYMPTOMS", font=("Cavolini", 16, "bold"))
        prediction_label.place(x=50, y=50)

        name_label = tk.Label(self.root, text="Enter your name", font=("Cavolini", 14))
        name_label.place(x=100, y=200)

        name_entry = tk.Entry(self.root, textvariable=self.user_name, font=("Cavolini", 14))
        name_entry.place(x=250, y=200)

        age_label = tk.Label(self.root, text="Enter age(10-70)", font=("Cavolini", 14))
        age_label.place(x=100, y=240)

        age_entry = tk.Entry(self.root, textvariable=self.user_age, font=("Cavolini", 14))
        age_entry.place(x=250, y=240)

        phone_label = tk.Label(self.root, text="Enter your phone number (10 digits):", font=("Cavolini", 14))
        phone_label.place(x=100, y=280)

        phone_entry = tk.Entry(self.root, textvariable=self.user_phone, font=("Cavolini", 14))
        phone_entry.place(x=250, y=280)

        submit_button = tk.Button(self.root, text="Submit", command=self.open_new_window, font=("Cavolini", 14))
        submit_button.place(x=250, y=320)
        exit_button = tk.Button(self.root, text="Exit", command=self.root.destroy, font=("Cavolini", 14))
        exit_button.place(x=350, y=320)

    def open_new_window(self):
        try:
            age = int(self.user_age.get())
            phone = int(self.user_phone.get())

            if 10 <= age <= 70 and len(str(phone)) == 10:
                messagebox.showinfo("Success", f"Thank you, {self.user_name.get()}! Details submitted successfully.")
               
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()

                new_window = tk.Toplevel()
                new_window.title("Select Symptoms")
                new_window.geometry("800x500")

                # Calculate the center coordinates for the new window
                center_x = int((screen_width - 800) / 2)
                center_y = int((screen_height - 500) / 2)

                # Set the geometry of the new window to open at the center
                new_window.geometry(f"800x500+{center_x}+{center_y}")
                new_window.resizable(False, False)

                label = tk.Label(new_window, text="Select Symptoms", font=("Cavolini", 16, "bold"))
                label.pack(pady=10)

                scrollbar = tk.Scrollbar(new_window, orient=tk.VERTICAL)
                symptoms_listbox = tk.Listbox(new_window, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, font=("Cavolini", 12))

                for symptom in df.columns[:-1]:
                    symptoms_listbox.insert(tk.END, symptom)

                scrollbar.config(command=symptoms_listbox.yview)

                symptoms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                selected_symptoms_label = tk.Label(new_window, text="Selected Symptoms:", font=("Cavolini", 12))
                selected_symptoms_label.pack(pady=10)

                def get_selected_symptoms():
                    selected_indices = symptoms_listbox.curselection()
                    self.selected_symptoms = [symptoms_listbox.get(index) for index in selected_indices]
                    selected_symptoms_label.config(text="Selected Symptoms:\n" + "\n".join(self.selected_symptoms))

                    # Enable the Predict button after selecting symptoms
                    predict_button.config(state=tk.NORMAL)

                select_button = tk.Button(new_window, text="Select", command=get_selected_symptoms, font=("Cavolini", 12))
                select_button.pack(pady=10)

                def predict_disease():
                    if self.selected_symptoms:
                        # Create a DataFrame with zeros for all symptoms
                        user_input = pd.DataFrame(0, index=range(len(self.selected_symptoms)), columns=X.columns)

                        # Set 1 for the selected symptoms
                        for symptom in self.selected_symptoms:
                            if symptom in user_input.columns:
                                user_input[symptom] = 1
                            else:
                                print(f"Ignoring invalid symptom: {symptom}")

                        # Predict the disease
                        self.predicted_disease = model.predict(user_input)
                        result_label.config(text=f"Predicted Disease: {self.predicted_disease[0]}")

                        # Enable the Save and Email buttons after prediction
                        save_button.config(state=tk.NORMAL)
                        email_button.config(state=tk.NORMAL)
                    else:
                        messagebox.showwarning("Warning", "Please select symptoms before predicting.")

                predict_button = tk.Button(new_window, text="Predict", command=predict_disease, font=("Cavolini", 12), state=tk.DISABLED)
                predict_button.pack(pady=10)

                output_label = tk.Label(new_window, text="Prediction Output:", font=("Cavolini", 14, "bold"))
                output_label.pack(pady=10)

                result_label = tk.Label(new_window, text="", font=("Cavolini", 14))
                result_label.pack(pady=10)

                # Save and Email buttons
                save_button = tk.Button(new_window, text="Save as PDF", command=lambda: self.save_as_pdf(new_window), font=("Cavolini", 12), state=tk.DISABLED)
                save_button.pack(pady=10)

                email_button = tk.Button(new_window, text="Email Report", command=self.email_report, font=("Cavolini", 12), state=tk.DISABLED)
                email_button.pack(pady=10)

                new_window.mainloop()
            else:
                messagebox.showerror("Error", "Invalid age or phone number. Please check and try again.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers for age and phone number.")

    def save_as_pdf(self, new_window):
        pdf_filename = f"Prediction_Report_{self.user_name.get()}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="MEDIMATRIX - Prediction Report", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Patient Name: {self.user_name.get()}", ln=True)
        pdf.cell(200, 10, txt=f"Patient Age: {self.user_age.get()}", ln=True)
        pdf.cell(200, 10, txt=f"Patient Phone: {self.user_phone.get()}", ln=True)
        pdf.cell(200, 10, txt=f"Selected Symptoms: {', '.join(self.selected_symptoms)}", ln=True)
        pdf.cell(200, 10, txt=f"Predicted Disease: {self.predicted_disease[0]}", ln=True)

        # Starting position for the multi-line text
        y_position = pdf.get_y()

        # Health Suggestions text
        health_suggestions_text = (
            "Health Suggestions: Your health is important. It is recommended to consult a healthcare professional for a detailed evaluation and follow their advice."
        )
        pdf.multi_cell(0, 10, txt=health_suggestions_text)

        # Other multi-line texts
        additional_texts = [
            "We also want to highlight the benefits of incorporating Ayurvedic Indian home supplies into your daily routine.",
            "Ayurvedic remedies often include herbs, spices, and other natural ingredients.",
            "Similarly, black pepper is not just a spice but also has potential health benefits.",
            "Explore the diverse range of Indian medicinal elements like neem, ginger, and holy basil.",
            "Additionally, Ayurveda recognizes the importance of individualized health plans based on your unique constitution (dosha).",
            f"Thank you, {self.user_name.get()}, for visiting Medi Matrix. We wish you good health and success on your journey to well-being, whether through traditional medical advice or holistic approaches like Ayurveda."
        ]
        for text in additional_texts:
            pdf.multi_cell(0, 10, txt=text)

        pdf.output(pdf_filename)
        messagebox.showinfo("Save as PDF", f"Report saved as {pdf_filename}")

        # Close the new window after saving the PDF
        # new_window.destroy()


    def email_report(self):
        email_address = simpledialog.askstring("Email Address", "Enter your email address:")
        if email_address:
            subject = "MEDIMATRIX - Prediction Report"
            body = (
                f"Patient Name: {self.user_name.get()}\n"
                f"Patient Age: {self.user_age.get()}\n"
                f"Patient Phone: {self.user_phone.get()}\n"
                f"\n\nHealth Suggestions: Your health is important. It is recommended to consult a healthcare professional for a detailed evaluation and follow their advice."
                f"\n\nThank you, {self.user_name.get()}, for visiting Medi Matrix. We wish you good health."
                f"\n\n\n This project is under testing AND IMPROVEMENT:- and this this projevct is made by:-\nD.RUTHWIKK-E22CSEU0230\nCH.TRILOKESH-E22CSEU0221\nK.MADHAVAN-E22CSEU0240\nN.SUBODH-E22CSEU0225"

            )

            try:
                # Save the PDF report before sending the email
                pdf_filename = f"Prediction_Report_{self.user_name.get()}.pdf"
                self.save_as_pdf(self.root)

                # Attach the PDF to the email
                attachments = [pdf_filename]
                self.send_email(email_address, subject, body, attachments)

                messagebox.showinfo("Email Report", "Report sent successfully.")
                
            except Exception as e:
                messagebox.showerror("Email Report", f"Error sending email: {str(e)}")
            
        else:
            messagebox.showwarning("Email Report", "Email address cannot be empty.")
        
        # self.open_new_window()
        # GUIPage(root, "inpageo.png", "wlco.jpg", "intro.mp4")
        
    def send_email(self, to_address, subject, body, attachments=None):
    # Configure your email settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "medimatrix.co@gmail.com"  # Replace with your email address
        smtp_password = "salc oiqf uowq hkir"  # Replace with your email password

    # Create the email message
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = to_address
        message["Subject"] = subject

    # Attach the body of the email
        message.attach(MIMEText(body, "plain"))

    # Attachments
        if attachments:
            for attachment in attachments:
                with open(attachment, "rb") as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {attachment}")
                message.attach(part)

        try:
        # Connect to the SMTP server and send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, to_address, message.as_string())

        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Email Error", "SMTP Authentication Error: Please check your email credentials.")
        except smtplib.SMTPException as e:
            messagebox.showerror("Email Error", f"SMTP Exception: {str(e)}")
        except Exception as e:
            messagebox.showerror("Email Error", f"Error sending email: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    gui_page = GUIPage(root, "inpageo.png", "wlco.jpg", "intro.mp4")
    root.mainloop()

