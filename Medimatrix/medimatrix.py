import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import pandas as pd
from tkinter import messagebox, Scrollbar, Listbox

df = pd.read_csv('Training.csv')

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

                scrollbar = Scrollbar(new_window, orient=tk.VERTICAL)
                symptoms_listbox = Listbox(new_window, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, font=("Cavolini", 12))

                for symptom in df.columns[:-1]:
                    symptoms_listbox.insert(tk.END, symptom)

                scrollbar.config(command=symptoms_listbox.yview)

                symptoms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                selected_symptoms_label = tk.Label(new_window, text="Selected Symptoms:", font=("Cavolini", 12))
                selected_symptoms_label.pack(pady=10)

                def get_selected_symptoms():
                    selected_indices = symptoms_listbox.curselection()
                    selected_symptoms = [symptoms_listbox.get(index) for index in selected_indices]
                    selected_symptoms_label.config(text="Selected Symptoms:\n" + "\n".join(selected_symptoms))
                    

                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                center_x = int((screen_width - 800) / 2)
                center_y = int((screen_height - 500) / 2)
                self.root.geometry(f"800x500+{center_x}+{center_y}")
                self.root.resizable(False, False)
                select_button = tk.Button(new_window, text="Select", command=get_selected_symptoms, font=("Cavolini", 12))
                select_button.pack(pady=10)
                def predict_disease():
                    selected_indices = symptoms_listbox.curselection()
                    selected_symptoms = [symptoms_listbox.get(index) for index in selected_indices]

                    # Create a DataFrame with zeros for all symptoms
                    user_input = pd.DataFrame(0, index=range(len(selected_symptoms)), columns=X.columns)

                    # Set 1 for the selected symptoms
                    for symptom in selected_symptoms:
                        if symptom in user_input.columns:
                            user_input[symptom] = 1
                        else:
                            print(f"Ignoring invalid symptom: {symptom}")

                    # Predict the disease
                    prediction = model.predict(user_input)
                    messagebox.showinfo("Prediction", f"Predicted Disease: {prediction[0]}")

                predict_button = tk.Button(new_window, text="Predict", command=predict_disease, font=("Cavolini", 12), state=tk.DISABLED)
                predict_button.pack(pady=10)
                new_window.mainloop()
            else:
                messagebox.showerror("Error", "Invalid age or phone number. Please check and try again.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers for age and phone number.")

if __name__ == "__main__":
    root = tk.Tk()
    gui_page = GUIPage(root, "inpageo.png", "wlco.jpg", "intro.mp4")
    root.mainloop()
