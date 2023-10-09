import sys, os, traceback, datetime

from PIL import Image, ImageTk
import tkinter as tki
from tkinter import messagebox, filedialog, ttk
from ttkthemes import themed_tk as tk
import pandas as pd
import numpy as np
import scipy.stats as stats



# Get working directory (for pyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class MainWindow(tk.ThemedTk):
    def __init__(self):
        tk.ThemedTk.__init__(self, themebg=True)
        self.st = "plastik"
        self.set_theme(self.st)
        self.screenW = self.winfo_screenwidth()
        self.screenH = self.winfo_screenheight()

        bW = self.screenW * 0.34
        bH = self.screenH * 0.18
        sW = int(self.screenW / 2)-self.screenW * 0.18
        self.geometry("%dx%d+%d+100" % (bW, bH, sW))
        self.resizable(False, False)
        self.wm_title("gravSolver v1.0")
        try:
            self.iconbitmap(resource_path("assets/gravsolverLogo.ico"))
        except:
            pass

        self.bind("<Escape>", lambda e: self.on_close())
        self.protocol("WM_DELETE_WINDOW", self.on_close)


        # Symbols
        self.syms0post2 = 'σ\u0302\N{SUPERSCRIPT TWO}\N{SUBSCRIPT ZERO}'
        self.syms0pr2 = 'σ\N{SUPERSCRIPT TWO}\N{SUBSCRIPT ZERO}'
        self.syms0post = 'σ\u0302\N{SUBSCRIPT ZERO}'
        self.syms0pr = 'σ\N{SUBSCRIPT ZERO}'
        self.symHo = 'H\N{SUBSCRIPT ZERO}'
        self.symHa = 'Hₐ'


        self.image_folder = ImageTk.PhotoImage(Image.open(resource_path("assets/folder.png")).resize((20, 20)))
        self.image_null = ImageTk.PhotoImage(Image.open(resource_path("assets/null.png")).resize((18, 18)))
        self.image_check = ImageTk.PhotoImage(Image.open(resource_path("assets/check.png")).resize((18, 18)))
        self.image_x = ImageTk.PhotoImage(Image.open(resource_path("assets/x.png")).resize((18, 18)))
        self.image_calc = ImageTk.PhotoImage(Image.open(resource_path("assets/calc.png")).resize((20, 20)))


        self.frame = ttk.Labelframe(self, text= " Settings ")
        self.frame.place(relx=0.01, rely=0.02, relheight=0.66, relwidth=0.98)

        # 1 Row
        self.label_file = ttk.Label(self.frame, text= "• Data file:").place(relx= 0.01, rely= 0.08, relheight= 0.28, relwidth= 0.16)

        self.btn_file = ttk.Button(self.frame, image= self.image_folder, cursor="hand2", command=lambda: self.readcsv())
        self.btn_file.place(relx= 0.18, rely= 0.08, relheight= 0.34, relwidth= 0.12)

        self.check_file = ttk.Label(self.frame, image= self.image_null)
        self.check_file.place(relx= 0.34, rely= 0.1, relheight= 0.28, relwidth= 0.06)


        self._m = 0
        self._m_var = tki.IntVar(value= self._m)
        self.label_m = ttk.Label(self.frame, text= "• m:").place(relx= 0.01, rely= 0.62, relheight= 0.28, relwidth= 0.08)
        self.label_m_val = ttk.Label(self.frame, textvariable= self._m_var).place(relx= 0.07, rely= 0.62, relheight= 0.28, relwidth= 0.15)

        self._n = 0
        self._n_var = tki.IntVar(value= self._n)
        self.label_n = ttk.Label(self.frame, text= "• n:").place(relx= 0.17, rely= 0.62, relheight= 0.28, relwidth= 0.08)
        self.label_n_val = ttk.Label(self.frame, textvariable= self._n_var).place(relx= 0.23, rely= 0.62, relheight= 0.28, relwidth= 0.15)

        self._r = 0
        self._r_var = tki.IntVar(value= self._r)
        self.label_r = ttk.Label(self.frame, text= "• r:").place(relx= 0.33, rely= 0.62, relheight= 0.28, relwidth= 0.08)
        self.label_r_val = ttk.Label(self.frame, textvariable= self._r_var).place(relx= 0.39, rely= 0.62, relheight= 0.28, relwidth= 0.11)


        self.s0_prior = 1
        self.s0_prior_var = tki.DoubleVar(value= self.s0_prior)
        self.label_s0_prior = ttk.Label(self.frame, text= f"• {self.syms0pr}:").place(relx= 0.77, rely= 0.09, relheight= 0.28, relwidth=0.12)
        self.entry_s0_prior = ttk.Entry(self.frame, textvariable=self.s0_prior_var, justify= "center")
        self.entry_s0_prior.place(relx= 0.85, rely= 0.09, relheight= 0.28, relwidth= 0.13)

        self.conf_level = 95
        self.conf_level_var = tki.DoubleVar(value= self.conf_level)
        self.label_conf_level = ttk.Label(self.frame, text= "• Confidence Level %:").place(relx= 0.55, rely= 0.62, relheight= 0.28, relwidth=0.3)
        self.entry_conf_level = ttk.Entry(self.frame, textvariable=self.conf_level_var, justify= "center")
        self.entry_conf_level.place(relx= 0.85, rely= 0.62, relheight= 0.28, relwidth= 0.13)

        
        self.btn_solve = ttk.Button(self, image= self.image_calc, cursor="hand2", command=lambda: self.solve())
        self.btn_solve.place(relx= 0.72, rely= 0.76, relheight= 0.2, relwidth= 0.12)

        self.btn_exit = ttk.Button(self, image= self.image_x, cursor="hand2", command=lambda: self.on_close())
        self.btn_exit.place(relx= 0.87, rely= 0.76, relheight= 0.2, relwidth= 0.12)

        self.create_folders()



    def readcsv(self):
        self.filename = filedialog.askopenfilename(initialdir= ".", filetypes=[(
            "CSV document", "*.csv"), ("Microsoft Excel Worksheet", "*.xlsx *.xls"), ("OpenDocument Spreadsheet ", "*.ods")])

        if self.filename:
            try:
                splitted_fname = self.filename.split("/")
                fname = splitted_fname[-1].split(".")
                ftype = fname[-1]

                if ftype == "csv":
                    self.data = pd.read_csv(self.filename)
                else:
                    self.data = pd.read_excel(self.filename)

                column_names = list(self.data.columns)
                if len(column_names) == 4 and all(elem in column_names for elem in ["id", "reading", "t", "std"]):
                    self.check_file.config(image= self.image_check)

                    # Regression variables
                    self.ids = self.data['id'].unique().tolist()
                    self.len_ids = len(self.ids)

                    self.x_ids = self.ids + ["d"]

                    self._m = len(self.x_ids)
                    self._n = len(self.data)
                    self._r = self._n - self._m

                    self._m_var.set(self._m)
                    self._n_var.set(self._n)
                    self._r_var.set(self._r)

                    # messagebox.showinfo("Info", "Data file has been imported successfully!")
                else:
                    self.check_file.config(image= self.image_null)
                    messagebox.showerror("Error", "Wrong format. Use:\nid | reading | t | std\ncolumns.")
            
            except Exception as e:
                self.check_file.config(image= self.image_null)
                ex = f"Error: Import data file:\n{traceback.format_exc()}\n" + str(e)
                log_filename = self.write_log(ex)
                messagebox.showerror("Error", f"Failed to import data file.\nFor more info check:\n{log_filename}")


    def make_table_A(self, df, ids, table_A):
        index = df.name
        id_index = ids.index(df['id'])
        table_A[index][id_index] = 1

    
    def solve(self):
        try:
            self.s0_prior = self.s0_prior_var.get()
            self.conf_level = self.conf_level_var.get()
            if self.conf_level > 99:
                self.conf_level = 99
                self.conf_level_var.set(self.conf_level)

            # Significance level α
            self.aval100 = 100 - self.conf_level
            self.aval = self.aval100 / 100

            self.s0_prior2 = self.s0_prior**2

            # Calculate t - t0
            self._t0 = self.data['t'].iloc[0]
            self.data['dt'] = self.data['t'] - self._t0

            # Calculate weights
            self.data['std2'] = self.data['std']**2
            self.data['p'] = self.s0_prior2 / self.data['std2']

            # Make tables
            # Calculate table A and At
            self.table_A = np.zeros((self._n, self.len_ids))
            self.data.apply(self.make_table_A, axis= 1, args= [self.ids, self.table_A])

            self.table_A = np.append(self.table_A, self.data['dt'].to_numpy().reshape((self._n, 1)), axis= 1)
            self.table_A_trans = self.table_A.transpose()

            # Calculate table P
            self.table_P = np.diag(self.data['p'].to_numpy())

            # Calculate table dl
            self.table_dl = self.data['reading'].to_numpy().reshape((self._n, 1))
            
            # Calculate table N = At * A and N-1
            self.table_N = np.dot(np.dot(self.table_A_trans, self.table_P), self.table_A)
            detN = np.linalg.det(self.table_N)
            if detN != 0:
                self.table_N_inv = np.linalg.inv(self.table_N)
            else:
                self.table_N_inv = np.linalg.pinv(self.table_N)

            # Calculate table U = At * dl
            self.table_U = np.dot(np.dot(self.table_A_trans, self.table_P), self.table_dl)

            # Calculate table X = N-1 * U
            self.table_X = np.dot(self.table_N_inv, self.table_U)

            # Calculate table dl_bar = A * X
            self.table_lbar = np.dot(self.table_A, self.table_X)

            # Calculate table of residuals υ = dl_bar - dl
            self.table_res = self.table_lbar - self.table_dl
            self.table_res_trans = self.table_res.transpose()

            # Calculate variance σ² (a posteriori)
            self.s0_post2 = (np.dot(np.dot(self.table_res_trans, self.table_P), self.table_res) / self._r)[0][0]
            self.s0_post = np.round(np.sqrt(self.s0_post2), 5)

            # Calculate varcovar table Vx = σ² * N-1 (a posteriori)
            self.table_varcovar_post = self.s0_post2 * self.table_N_inv

            # Calculate coord stds σ (m)
            self.stds = np.sqrt(np.diagonal(self.table_varcovar_post))

            # Final dataframe
            self.final_values = pd.DataFrame(self.x_ids, columns= ['id'])
            self.final_values['X'] = np.round(self.table_X, 5).flatten().tolist()
            self.final_values[f'σX'] = np.round(self.stds, 5)

            now = datetime.datetime.now()
            now_txt = now.strftime("%Y-%m-%d %H:%M:%S")
            now_file = now.strftime("%Y.%m.%d_%H.%M.%S")
            self.final_values.to_csv(f"{self.report_dir}/{now_file}_results.csv", index= False)

            # Statistical F - test
            # Null hypothesis: s0_post2 = s0_prior2
            # Alternative hypothesis: s0_post2 != s0_prior2
            # Two - tailed
            # fdistribution = stats.f(self._m - 1, self._m - 1)
            fdistribution = stats.f(self._r, self._r)
            
            upper_tt = 1 - self.aval / 2
            lower_tt = self.aval / 2
            fstatistics_tt = self.s0_post2 / self.s0_prior2

            p_value_tt = 2 * min(fdistribution.cdf(fstatistics_tt), 1 - fdistribution.cdf(fstatistics_tt))
            p_value_str_tt = f"{round(p_value_tt * 100, 3)} %"

            f_upper_tt = round(fdistribution.ppf(upper_tt), 5)
            f_lower_tt = round(fdistribution.ppf(lower_tt), 5)

            can_reject_tt = f"Null Hypothesis {self.symHo} accepted ✔️"
            if p_value_tt < self.aval and (fstatistics_tt > f_upper_tt or fstatistics_tt < f_lower_tt):
                can_reject_tt = f"Null Hypothesis {self.symHo} rejected ❌"    

            # Upper - tailed
            # Null hypothesis: s0_post2 <= s0_prior2
            # Alternative hypothesis: s0_post2 > s0_prior2 
            # Meta thn synorthosi panta s0_post2 < s0_prior2 !!!
            upper_ut = 1 - self.aval
            fstatistics_ut = max(self.s0_post2, self.s0_prior2) / min(self.s0_post2, self.s0_prior2)
            p_value_ut = 1 - fdistribution.cdf(fstatistics_ut)
            p_value_str_ut = f"{round(p_value_ut * 100, 3)} %"
            f_upper_ut = round(fdistribution.ppf(upper_ut), 5)

            fratio_ut = f"{self.syms0post2}/{self.syms0pr2}" if fstatistics_ut == fstatistics_tt else f"{self.syms0pr2}/{self.syms0post2}"

            can_reject_ut = f"Null Hypothesis {self.symHo} accepted ✔️"
            if p_value_ut < self.aval and fstatistics_ut > f_upper_ut:
                can_reject_ut = f"Null Hypothesis {self.symHo} rejected ❌" 

            # Lower - tailed
            # Null hypothesis: s0_post2 >= s0_prior2
            # Alternative hypothesis: s0_post2 < s0_prior2
            # Lower - tailed
            lower_lt = self.aval
            fstatistics_lt = min(self.s0_post2, self.s0_prior2) / max(self.s0_post2, self.s0_prior2)
            p_value_lt = fdistribution.cdf(fstatistics_lt)
            p_value_str_lt = f"{round(p_value_lt * 100, 3)} %"
            f_lower_lt = round(fdistribution.ppf(lower_lt), 5)

            fratio_lt = f"{self.syms0post2}/{self.syms0pr2}" if fstatistics_lt == fstatistics_tt else f"{self.syms0pr2}/{self.syms0post2}"

            can_reject_lt = f"Null Hypothesis {self.symHo} accepted ✔️"
            if p_value_lt < self.aval and fstatistics_lt < f_lower_lt:
                can_reject_lt = f"Null Hypothesis {self.symHo} rejected ❌" 


            # Make report
            txt_report = f"<* gravSolver v1.0 - Regression Analysis Report *>\nDate: {now_txt}\nRegression method: Ordinary Least Squares\n"
            txt_report += f"a priori {self.syms0pr}: {round(self.s0_prior, 5)}\na posteriori {self.syms0post}: {round(self.s0_post, 5)}\n"
            txt_report += f"Confidence level: {self.conf_level}%\nSignificance level α: {self.aval100}%\n"
            txt_report += f"Sample size: {self._n}\nParameters: {self._m}\nDegrees of freedom: {self._r}\n"

            txt_report += f"\nTest method #1: Two-tailed F-test\nNull Hypothesis {self.symHo}: {self.syms0post} = {self.syms0pr}\n"
            txt_report += f"Alternative Hypothesis {self.symHa}: {self.syms0post} ≠ {self.syms0pr}\n"
            txt_report += f"F = {self.syms0post2}/{self.syms0pr2}: {round(fstatistics_tt, 5)}\n"
            txt_report += f"F_lower: {f_lower_tt}\nF_upper: {f_upper_tt}\np-value: {round(p_value_tt, 5)}\n"
            txt_report += f"Result: {can_reject_tt}\n"

            txt_report += f"\nTest method #2: Upper-tailed F-test\nNull Hypothesis {self.symHo}: {self.syms0post} ≤ {self.syms0pr}\n"
            txt_report += f"Alternative Hypothesis {self.symHa}: {self.syms0post} > {self.syms0pr}\n"
            txt_report += f"F = {fratio_ut}: {round(fstatistics_ut, 5)}\n"
            txt_report += f"F_upper: {f_upper_ut}\np-value: {round(p_value_ut, 5)}\n"
            txt_report += f"Result: {can_reject_ut}\n"

            txt_report += f"\nTest method #3: Lower-tailed F-test\nNull Hypothesis {self.symHo}: {self.syms0post} ≥ {self.syms0pr}\n"
            txt_report += f"Alternative Hypothesis {self.symHa}: {self.syms0post} < {self.syms0pr}\n"
            txt_report += f"F = {fratio_lt}: {round(fstatistics_lt, 5)}\n"
            txt_report += f"F_lower: {f_lower_lt}\np-value: {round(p_value_lt, 5)}\n"
            txt_report += f"Result: {can_reject_lt}\n"

            with open(f"{self.report_dir}/{now_file}_stats.txt", "w") as file:
                file.write(txt_report)
            
            messagebox.showinfo("Info", "Regression solved successfully!\nCheck results at 01_exports folder.")
        except Exception as e:
            ex = f"Error: Solve regression:\n{traceback.format_exc()}\n" + str(e)
            log_filename = self.write_log(ex)
            messagebox.showerror("Error", f"Failed to solve regression.\nFor more info check:\n{log_filename}")


    # Create directories
    def create_dir(self, dirname):
        try:
            if getattr(sys, "frozen", False):
                self.current_dir = os.path.dirname(sys.executable).replace('\\', '/')
            elif __file__:
                self.current_dir = os.path.dirname(__file__).replace('\\', '/')
            
            new_dir = f"{self.current_dir}/{dirname}"
            new_dir_exists = os.path.isdir(new_dir)

            if not new_dir_exists:
                os.mkdir(new_dir)
            
            return({"success": new_dir})
        except Exception as e:
            ex = f"Error: Create directory:\n{traceback.format_exc()}\n"
            print(ex)
            return({"error": ex + str(e)})

    # Create app folders
    def create_folders(self):
        log_dir = self.create_dir("00_logs")
        if "error" in log_dir:
            log_filename = self.write_log(log_dir['error'])
            messagebox.showerror("Error", f"Failed to create logs directory.\nFor more info check:\n{log_filename}")
        else:
            self.log_dir = log_dir['success']

        report_dir = self.create_dir("01_exports")
        if "error" in report_dir:
            log_filename = self.write_log(report_dir['error'])
            messagebox.showerror("Error", f"Failed to create exports directory.\nFor more info check:\n{log_filename}")
        else:
            self.report_dir = report_dir['success']
    
    # Create logs
    def write_log(self, error):
        now = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        day = now.split("_")[0]

        day_log_dir = f"{self.log_dir}/{day}"
        day_log_dir_exists = os.path.isdir(day_log_dir)
        if not day_log_dir_exists:
            os.mkdir(day_log_dir)

        log_filename = f"{day_log_dir}/{now}_error.log"

        with open(log_filename, "a") as file:
            try:
                file.write(error)
            except:
                file.write(str(error))

        return(log_filename)

    def on_close(self):
        self.killThread = True
        self.destroy()
        os._exit(0)


    


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
