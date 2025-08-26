import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, filedialog
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# NOTE: You will need to install the following libraries for this code to run:
# pip install pandas matplotlib seaborn openpyxl ReportLab

# --- Configuration ---
CSV_FILE = "finance_tracker.csv"
COLUMNS = ["date", "type", "category", "amount", "description"]
CATEGORIES = {
    "Expense": ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other Expense"],
    "Income": ["Salary", "Bonus", "Investment", "Gift", "Other Income"]
}

# --- GUI Application Class ---
class FinanceTrackerApp(tk.Tk):
    """
    Main application window for the Personal Finance Tracker.
    """
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (800 / 2)
        y = (screen_height / 2) - (600 / 2)
        self.geometry(f'+{int(x)}+{int(y)}')

        # Load data on startup
        self.data = self.load_data()
        
        self.create_widgets()
        
    def load_data(self):
        """
        Loads data from the CSV file into a pandas DataFrame.
        If the file doesn't exist, an empty DataFrame is returned.
        """
        if os.path.exists(CSV_FILE):
            return pd.read_csv(CSV_FILE)
        return pd.DataFrame(columns=COLUMNS)

    def create_widgets(self):
        """
        Builds the user interface using a Notebook (tabbed layout).
        """
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        # Create and add frames for each tab
        self.add_record_frame = self.create_add_record_frame(self.notebook)
        self.history_frame = self.create_history_frame(self.notebook)
        self.dashboard_frame = self.create_dashboard_frame(self.notebook)

        self.notebook.add(self.add_record_frame, text="Add Record")
        self.notebook.add(self.history_frame, text="History")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Bind the notebook tab change event to update dashboard and history
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Create menu bar for export functionality
        self.create_menu()

    def create_menu(self):
        """
        Creates a file menu for exporting data.
        """
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to Excel", command=self.export_to_excel)
        file_menu.add_command(label="Export to PDF", command=self.export_to_pdf)

    def create_add_record_frame(self, parent):
        """
        Creates the 'Add Record' tab GUI.
        """
        frame = ttk.Frame(parent, padding="20")
        
        title_label = ttk.Label(frame, text="Add New Record", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Radio buttons for type
        type_frame = ttk.Frame(frame)
        type_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Label(type_frame, text="Type:").pack(side="left", padx=(0, 10))
        self.record_type = tk.StringVar(value="Expense")
        self.expense_radio = ttk.Radiobutton(type_frame, text="Expense", variable=self.record_type, value="Expense", command=self.update_categories)
        self.income_radio = ttk.Radiobutton(type_frame, text="Income", variable=self.record_type, value="Income", command=self.update_categories)
        self.expense_radio.pack(side="left")
        self.income_radio.pack(side="left")

        # Category dropdown
        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky="ew", pady=5)
        self.update_categories()

        # Amount entry
        ttk.Label(frame, text="Amount:").grid(row=3, column=0, sticky="w", pady=5)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=3, column=1, sticky="ew", pady=5)

        # Description entry
        ttk.Label(frame, text="Description:").grid(row=4, column=0, sticky="w", pady=5)
        self.description_entry = ttk.Entry(frame)
        self.description_entry.grid(row=4, column=1, sticky="ew", pady=5)

        # Save button
        save_button = ttk.Button(frame, text="Save Record", command=self.save_record)
        save_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)
        return frame

    def create_history_frame(self, parent):
        """
        Creates the 'History' tab with a Treeview for data display and filtering.
        """
        frame = ttk.Frame(parent, padding="20")

        # Filter controls
        filter_frame = ttk.LabelFrame(frame, text="Filter Records")
        filter_frame.pack(fill="x", pady=10)

        # Filter by Type
        ttk.Label(filter_frame, text="Type:").pack(side="left", padx=5)
        self.filter_type_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=["All", "Income", "Expense"], state="readonly").pack(side="left", padx=5)
        
        # Filter by Category
        ttk.Label(filter_frame, text="Category:").pack(side="left", padx=5)
        self.filter_category_var = tk.StringVar(value="All")
        # Combine all categories for the filter dropdown
        all_categories = ["All"] + CATEGORIES["Expense"] + CATEGORIES["Income"]
        ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=all_categories, state="readonly").pack(side="left", padx=5)
        
        # Filter button
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).pack(side="left", padx=5)
        
        # Treeview to display data
        self.treeview = ttk.Treeview(frame, columns=COLUMNS, show="headings")
        self.treeview.pack(fill="both", expand=True)

        for col in COLUMNS:
            self.treeview.heading(col, text=col.capitalize(), anchor="w")
            self.treeview.column(col, width=100)
            
        # Adjust column widths
        self.treeview.column("date", width=150)
        self.treeview.column("description", width=250)
        
        self.load_history_data()

        return frame

    def create_dashboard_frame(self, parent):
        """
        Creates the 'Dashboard' tab with data visualizations.
        """
        frame = ttk.Frame(parent, padding="20")
        
        # Placeholder for plots
        self.plot_frame = ttk.Frame(frame)
        self.plot_frame.pack(fill="both", expand=True)
        
        return frame
        
    def update_categories(self):
        """
        Updates the category dropdown list based on the selected record type.
        """
        current_type = self.record_type.get()
        self.category_combo['values'] = CATEGORIES.get(current_type, [])
        self.category_combo.set("")

    def save_record(self):
        """
        Retrieves data from the form, validates it, and saves it to a CSV file.
        """
        record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_type = self.record_type.get()
        category = self.category_var.get()
        amount_str = self.amount_entry.get().strip()
        description = self.description_entry.get().strip()

        # --- Input Validation ---
        if not category:
            messagebox.showerror("Validation Error", "Please select a category.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Validation Error", "Amount must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a valid number.")
            return
            
        new_record = {
            "date": [record_date],
            "type": [record_type],
            "category": [category],
            "amount": [amount],
            "description": [description]
        }
        
        new_df = pd.DataFrame(new_record, columns=COLUMNS)
        
        # Save data to CSV
        try:
            is_new_file = not os.path.exists(CSV_FILE)
            new_df.to_csv(CSV_FILE, index=False, mode='a', header=is_new_file)
            
            messagebox.showinfo("Success", "Record saved successfully!")
            
            # Update the in-memory data
            self.data = pd.concat([self.data, new_df], ignore_index=True)

            # Clear input fields
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.category_combo.set("")

        except Exception as e:
            messagebox.showerror("File Error", f"An error occurred while saving the file: {e}")

    def on_tab_change(self, event):
        """
        Refreshes content when the user switches tabs.
        """
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "History":
            self.load_history_data()
        elif current_tab == "Dashboard":
            self.create_dashboard_plots()
            
    def load_history_data(self, filtered_df=None):
        """
        Clears and repopulates the Treeview with data.
        """
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        df_to_display = filtered_df if filtered_df is not None else self.data
        
        if not df_to_display.empty:
            for index, row in df_to_display.iterrows():
                self.treeview.insert("", "end", values=list(row))

    def apply_filter(self):
        """
        Filters the data based on user selections and updates the Treeview.
        """
        filtered_data = self.data.copy()
        
        # Filter by type
        filter_type = self.filter_type_var.get()
        if filter_type != "All":
            filtered_data = filtered_data[filtered_data["type"] == filter_type]
            
        # Filter by category
        filter_category = self.filter_category_var.get()
        if filter_category != "All":
            filtered_data = filtered_data[filtered_data["category"] == filter_category]
            
        self.load_history_data(filtered_data)
        
    def create_dashboard_plots(self):
        """
        Generates and displays two plots on the dashboard:
        1. A pie chart of spending by category (for Expenses).
        2. A bar chart of monthly income vs. expense.
        """
        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if self.data.empty:
            ttk.Label(self.plot_frame, text="No data to display. Please add some records first.", font=("Helvetica", 12)).pack(pady=20)
            return
            
        # Pie chart for expenses by category
        try:
            expense_data = self.data[self.data['type'] == 'Expense'].groupby('category')['amount'].sum()
            if not expense_data.empty:
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                sns.set_palette("pastel")
                ax1.pie(expense_data, labels=expense_data.index, autopct='%1.1f%%', startangle=90)
                ax1.set_title("Expense Distribution by Category")
                ax1.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
                
                canvas1 = FigureCanvasTkAgg(fig1, master=self.plot_frame)
                canvas_widget1 = canvas1.get_tk_widget()
                canvas_widget1.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error generating pie chart: {e}")
            
        # Bar chart for monthly summary
        try:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data['month'] = self.data['date'].dt.to_period('M')
            
            monthly_summary = self.data.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
            
            if not monthly_summary.empty:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                monthly_summary.plot(kind='bar', ax=ax2)
                ax2.set_title("Monthly Income vs. Expense")
                ax2.set_xlabel("Month")
                ax2.set_ylabel("Amount")
                ax2.grid(axis='y', linestyle='--', alpha=0.7)
                
                canvas2 = FigureCanvasTkAgg(fig2, master=self.plot_frame)
                canvas_widget2 = canvas2.get_tk_widget()
                canvas_widget2.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error generating bar chart: {e}")

    def export_to_excel(self):
        """
        Exports the entire dataset to an Excel file.
        """
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                self.data.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        except ImportError:
            messagebox.showerror("Library Missing", "Please install the 'openpyxl' library: pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during Excel export: {e}")

    def export_to_pdf(self):
        """
        Exports the entire dataset to a PDF file.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors

            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []

                # Convert DataFrame to list of lists for ReportLab
                data_list = [self.data.columns.to_list()] + self.data.values.tolist()
                table = Table(data_list)
                
                # Style the table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)
                
                elements.append(table)
                doc.build(elements)
                messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        except ImportError:
            messagebox.showerror("Library Missing", "Please install the 'ReportLab' library: pip install ReportLab")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during PDF export: {e}")

if __name__ == "__main__":
    # Fix for HiDPI screens
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = FinanceTrackerApp()
    app.mainloop()

