# frontend.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from dmv import check_skills_course_a, check_skills_course_b, check_both_courses, load_user_data

# Set up the front-end GUI using tkinter
def run_gui():
    root = tk.Tk()
    root.title("DMV Road Test Scheduler Checker")
    root.geometry("450x550")
    root.configure(bg="#e0f7fa")

    # Load saved user data if available
    user_data = load_user_data() if load_user_data() else {}

    # Create a style for the widgets
    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12), background="#e0f7fa")
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=5)

    # Create a frame for the form
    form_frame = ttk.Frame(root, padding="10")
    form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="EW")

    # Create input fields
    ttk.Label(form_frame, text="License Permit Number:").grid(row=0, column=0, padx=10, pady=5, sticky="W")
    permit_number = ttk.Entry(form_frame)
    permit_number.insert(0, user_data.get("permit_number", ""))
    permit_number.grid(row=0, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(form_frame, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
    last_name = ttk.Entry(form_frame)
    last_name.insert(0, user_data.get("last_name", ""))
    last_name.grid(row=1, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(form_frame, text="Date of Birth (MM/DD/YYYY):").grid(row=2, column=0, padx=10, pady=5, sticky="W")
    dob_entry = ttk.Entry(form_frame)
    dob_entry.insert(0, f"{user_data.get('dob_month', '')}/{user_data.get('dob_day', '')}/{user_data.get('dob_year', '')}")
    dob_entry.grid(row=2, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(form_frame, text="Zip Code:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
    zip_code = ttk.Entry(form_frame)
    zip_code.insert(0, user_data.get("zip_code", ""))
    zip_code.grid(row=3, column=1, padx=10, pady=5, sticky="W")

    # Create a status label to show waiting messages
    status_label = ttk.Label(root, text="", font=("Helvetica", 12), background="#e0f7fa", foreground="black")
    status_label.grid(row=2, column=0, padx=20, pady=5, sticky="W")

    # Function to handle form data and call the backend functions
    def parse_and_run(check_function):
        permit = permit_number.get()
        last = last_name.get()
        dob = dob_entry.get()
        zipc = zip_code.get()

        try:
            dob_month, dob_day, dob_year = dob.split('/')
        except ValueError:
            messagebox.showerror("Input Error", "Please enter the date of birth in MM/DD/YYYY format.")
            return

        status_label.config(text="Waiting...")
        root.update_idletasks()

        try:
            result = check_function(permit, last, dob_month, dob_day, dob_year, zipc)
            if isinstance(result, tuple):  # For checking both courses
                course_a_result, course_b_result = result
                if course_a_result:
                    messagebox.showinfo("Skills Course A: 1 Regan Ct. , Cranston, RI 02920", course_a_result)
                else:
                    messagebox.showinfo("Skills Course A", "No available dates found for Skills Course A.")
                if course_b_result:
                    messagebox.showinfo("Skills Course B: 600 New London Ave., Cranston, RI 02920", course_b_result)
                else:
                    messagebox.showinfo("Skills Course B", "No available dates found for Skills Course B.")
            else:  # For checking a single course
                if result:
                    messagebox.showinfo("Available Date", result)
                else:
                    messagebox.showinfo("No Availability", "No available dates found.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            status_label.config(text="")

    # Create a frame for the buttons
    button_frame = ttk.Frame(root, padding="10")
    button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="EW")

    # Buttons to handle different checks
    skill_a_button = ttk.Button(button_frame, text="Check Skills Course A", command=lambda: parse_and_run(check_skills_course_a))
    skill_a_button.grid(row=4, column=0, columnspan=2, pady=5, sticky="EW")

    skill_b_button = ttk.Button(button_frame, text="Check Skills Course B", command=lambda: parse_and_run(check_skills_course_b))
    skill_b_button.grid(row=5, column=0, columnspan=2, pady=5, sticky="EW")

    both_courses_button = ttk.Button(button_frame, text="Check Both Courses", command=lambda: parse_and_run(check_both_courses))
    both_courses_button.grid(row=6, column=0, columnspan=2, pady=5, sticky="EW")

    # Customize button colors
    style.configure("TButton", background="#00796b", foreground="black")

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    run_gui()
