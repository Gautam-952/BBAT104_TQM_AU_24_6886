import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta

from app.database.db import init_db
from app.services.usability_service import UsabilityService
from app.services.patient_service import (
    get_all_patients, create_patient, update_patient, delete_patient
)
from app.services.doctor_service import (
    get_all_doctors, create_doctor, update_doctor, delete_doctor
)
from app.services.appointment_service import (
    get_all_appointments, create_appointment, update_appointment, delete_appointment
)
from app.services.medical_record_service import (
    get_all_medical_records, create_medical_record,
    update_medical_record, delete_medical_record
)
from app.services.bill_service import (
    get_all_bills, create_bill, update_bill, delete_bill
)


FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_KPI    = ("Segoe UI", 22, "bold")
FONT_KPI_LB = ("Segoe UI", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")


class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.user_id = 1
        self.us = UsabilityService(self.user_id)
        self.tokens = self.us.get_tokens()

        self.title("Hospital Management System — BBAT104 TQM Q03")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=self.tokens["bg"])

        self._build_topbar()
        self._build_notebook()
        self._apply_theme()


    def _build_topbar(self):
        T = self.tokens
        self.topbar = tk.Frame(self, bg=T["bg_secondary"], pady=8)
        self.topbar.pack(fill=tk.X, side=tk.TOP)

        self.title_lbl = tk.Label(self.topbar, text="🏥  Hospital Management System",
                                  font=("Segoe UI", 14, "bold"),
                                  bg=T["bg_secondary"], fg=T["accent"])
        self.title_lbl.pack(side=tk.LEFT, padx=16)

        self.sub_lbl = tk.Label(self.topbar, text="BBAT104 TQM | Q03 Usability | Gautam Bisht",
                                font=FONT_SMALL, bg=T["bg_secondary"],
                                fg=T["text_muted"])
        self.sub_lbl.pack(side=tk.LEFT, padx=4)

        self.topbar_right = tk.Frame(self.topbar, bg=T["bg_secondary"])
        self.topbar_right.pack(side=tk.RIGHT, padx=12)

        self.theme_lbl = tk.Label(self.topbar_right, text="Theme:", font=FONT_SMALL,
                                  bg=T["bg_secondary"], fg=T["text_muted"])
        self.theme_lbl.pack(side=tk.LEFT, padx=(0, 4))

        self.theme_var = tk.StringVar(value="Clinical Blue")
        self.theme_combo = ttk.Combobox(self.topbar_right, textvariable=self.theme_var,
                                        values=self.us.available_themes(),
                                        width=16, state="readonly",
                                        font=FONT_SMALL)
        self.theme_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)

        self.dark_btn = tk.Button(self.topbar_right, text="🌙  Dark Mode",
                                  font=FONT_SMALL, relief=tk.FLAT, cursor="hand2",
                                  command=self._toggle_dark,
                                  bg=T["accent"], fg="#ffffff",
                                  activebackground=T["accent_hover"],
                                  padx=10, pady=4)
        self.dark_btn.pack(side=tk.LEFT)


    def _build_notebook(self):
        self.style = ttk.Style(self)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.tab_dash    = self._tab("📊 Dashboard")
        self.tab_pat     = self._tab("🧑‍⚕️ Patients")
        self.tab_doc     = self._tab("👨‍⚕️ Doctors")
        self.tab_appt    = self._tab("📅 Appointments")
        self.tab_rec     = self._tab("📋 Medical Records")
        self.tab_bill    = self._tab("💳 Billing")
        self.tab_cal     = self._tab("🗓️ Calendar")

        self._build_dashboard(self.tab_dash)
        self._build_patients(self.tab_pat)
        self._build_doctors(self.tab_doc)
        self._build_appointments(self.tab_appt)
        self._build_records(self.tab_rec)
        self._build_billing(self.tab_bill)
        self._build_calendar(self.tab_cal)

    def _tab(self, label: str) -> tk.Frame:
        frame = tk.Frame(self.nb)
        self.nb.add(frame, text=f"  {label}  ")
        return frame


    def _apply_theme(self):
        T = self.tokens
        self.configure(bg=T["bg"])
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=T["bg_secondary"],
                             borderwidth=0, tabmargins=[0, 4, 0, 0])
        self.style.configure("TNotebook.Tab",
                             background=T["bg_secondary"],
                             foreground=T["text_muted"],
                             font=("Segoe UI", 10, "bold"),
                             padding=[12, 6])
        self.style.map("TNotebook.Tab",
                       background=[("selected", T["bg"])],
                       foreground=[("selected", T["accent"])])
        self.style.configure("Treeview",
                             background=T["bg_card"],
                             foreground=T["text"],
                             fieldbackground=T["bg_card"],
                             rowheight=26,
                             font=FONT_SMALL)
        self.style.configure("Treeview.Heading",
                             background=T["bg_secondary"],
                             foreground=T["accent"],
                             font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", T["accent"])],
                       foreground=[("selected", "#ffffff")])
        self.style.configure("TCombobox", fieldbackground=T["bg_card"],
                             background=T["bg_card"], foreground=T["text"])
        self.style.configure("TScrollbar", background=T["bg_secondary"],
                             troughcolor=T["bg"])
        self._recolor_frames(self)
        self.topbar.configure(bg=T["bg_secondary"])
        if hasattr(self, "topbar_right"):
            self.topbar_right.configure(bg=T["bg_secondary"])
        if hasattr(self, "title_lbl"):
            self.title_lbl.configure(bg=T["bg_secondary"], fg=T["accent"])
        if hasattr(self, "sub_lbl"):
            self.sub_lbl.configure(bg=T["bg_secondary"], fg=T["text_muted"])
        if hasattr(self, "theme_lbl"):
            self.theme_lbl.configure(bg=T["bg_secondary"], fg=T["text_muted"])
        if hasattr(self, "dark_btn"):
            self.dark_btn.configure(bg=T["accent"], fg="#ffffff",
                                    activebackground=T["accent_hover"])
        self.nb.configure(style="TNotebook")

    def _recolor_frames(self, widget):
        if widget in (getattr(self, "topbar", None), getattr(self, "topbar_right", None)):
            return
        T = self.tokens
        try:
            if isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                widget.configure(bg=T["bg"])
            elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                widget.configure(bg=T["bg"], fg=T["text"])
            elif isinstance(widget, tk.Button) and not isinstance(widget, ttk.Button):
                widget.configure(bg=T["accent"], fg="#ffffff",
                                 activebackground=T["accent_hover"],
                                 activeforeground="#ffffff")
            elif isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Entry):
                widget.configure(bg=T["bg_card"], fg=T["text"],
                                 insertbackground=T["text"],
                                 relief=tk.FLAT, highlightthickness=1,
                                 highlightbackground=T["border"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=T["bg_card"], fg=T["text"],
                                 insertbackground=T["text"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._recolor_frames(child)

    def _on_theme_change(self, _event=None):
        name = self.theme_var.get()
        try:
            self.us.set_dark(True)
            self.tokens = self.us.set_theme(name)
            self._apply_theme()
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Theme Error", str(e))

    def _toggle_dark(self):
        self.tokens = self.us.toggle_dark()
        self._apply_theme()
        self._refresh_all()

    def _refresh_all(self):
        if hasattr(self, "_refresh_dash"):
            self._refresh_dash()
        if hasattr(self, "_refresh_pat"):
            self._refresh_pat()
        if hasattr(self, "_refresh_doc"):
            self._refresh_doc()
        if hasattr(self, "_refresh_appt"):
            self._refresh_appt()
        if hasattr(self, "_refresh_rec"):
            self._refresh_rec()
        if hasattr(self, "_refresh_bill"):
            self._refresh_bill()
        if hasattr(self, "_refresh_cal"):
            self._refresh_cal()


    def _section_label(self, parent, text):
        T = self.tokens
        lf = tk.Frame(parent, bg=T["bg"])
        lf.pack(fill=tk.X, padx=16, pady=(12, 2))
        tk.Label(lf, text=text, font=FONT_HEADER,
                 bg=T["bg"], fg=T["accent"]).pack(side=tk.LEFT)
        tk.Frame(lf, bg=T["border"], height=2).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=8)
        return lf

    def _btn(self, parent, text, cmd, color=None):
        T = self.tokens
        bg = color or T["accent"]
        b = tk.Button(parent, text=text, font=FONT_BTN, command=cmd,
                      bg=bg, fg="#ffffff", relief=tk.FLAT, cursor="hand2",
                      padx=12, pady=5,
                      activebackground=T["accent_hover"],
                      activeforeground="#ffffff")
        b.pack(side=tk.LEFT, padx=4)
        return b

    def _entry(self, parent, label, width=22):
        T = self.tokens
        f = tk.Frame(parent, bg=T["bg"])
        f.pack(side=tk.LEFT, padx=6)
        tk.Label(f, text=label, font=FONT_SMALL,
                 bg=T["bg"], fg=T["text_muted"]).pack(anchor=tk.W)
        e = tk.Entry(f, width=width, font=FONT_SMALL,
                     bg=T["bg_card"], fg=T["text"],
                     insertbackground=T["text"], relief=tk.FLAT,
                     highlightthickness=1,
                     highlightbackground=T["border"])
        e.pack()
        return e

    def _clear_entry(self, *entries):
        for e in entries:
            try:
                e.delete(0, tk.END)
            except Exception:
                pass

    def _tree(self, parent, cols, heights=16):
        T = self.tokens
        frame = tk.Frame(parent, bg=T["bg"])
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))

        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            height=heights, yscrollcommand=sb.set)
        sb.configure(command=tree.yview)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=max(80, 140 if len(col) > 10 else 100),
                        anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree


    def _build_dashboard(self, parent):
        T = self.tokens
        self._section_label(parent, "📊  Dashboard Overview")

        self.kpi_frame = tk.Frame(parent, bg=T["bg"])
        self.kpi_frame.pack(fill=tk.X, padx=16, pady=8)

        self.recent_frame = tk.Frame(parent, bg=T["bg"])
        self.recent_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        rf = tk.Button(parent, text="↻  Refresh Dashboard",
                       font=FONT_SMALL, relief=tk.FLAT, cursor="hand2",
                       command=self._refresh_dash,
                       bg=self.tokens["bg_secondary"],
                       fg=self.tokens["text_muted"], padx=8, pady=3)
        rf.pack(pady=(0, 8))

        self._refresh_dash()

    def _kpi_card(self, parent, title, value, color):
        T = self.tokens
        card = tk.Frame(parent, bg=T["bg_card"], padx=18, pady=14,
                        relief=tk.FLAT, bd=0)
        card.pack(side=tk.LEFT, padx=8, pady=4, fill=tk.BOTH, expand=True)

        bar = tk.Frame(card, bg=color, height=4)
        bar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(card, text=str(value), font=FONT_KPI,
                 bg=T["bg_card"], fg=color).pack()
        tk.Label(card, text=title, font=FONT_KPI_LB,
                 bg=T["bg_card"], fg=T["text_muted"]).pack()

    def _refresh_dash(self):
        T = self.tokens
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        for w in self.recent_frame.winfo_children():
            w.destroy()

        s = self.us.dashboard()
        cards = [
            ("Total Patients",       s["total_patients"],      T["accent"]),
            ("Total Doctors",        s["total_doctors"],        T["success"]),
            ("Today's Appts",        s["todays_appointments"],  T["warning"]),
            ("Scheduled Today",      s["scheduled_today"],      "#a855f7"),
            ("Pending Bills",        s["pending_bills"],        T["danger"]),
            ("Paid Bills",           s["paid_bills"],           T["success"]),
            ("Pending (Rs.)",        f"{s['pending_amount']:,.0f}", T["danger"]),
            ("Collected (Rs.)",      f"{s['paid_amount']:,.0f}", T["success"]),
        ]
        for title, val, color in cards:
            self._kpi_card(self.kpi_frame, title, val, color)

        left = tk.Frame(self.recent_frame, bg=T["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        right = tk.Frame(self.recent_frame, bg=T["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Recent Patients", font=FONT_HEADER,
                 bg=T["bg"], fg=T["text"]).pack(anchor=tk.W, pady=(4, 4))
        for p in s["recent_patients"]:
            tk.Label(left,
                     text=f"  {p['patient_code']}  {p['name']}  ({p['blood_group']})",
                     font=FONT_SMALL, bg=T["bg_card"], fg=T["text"],
                     anchor=tk.W, padx=8, pady=4).pack(fill=tk.X, pady=1)

        tk.Label(right, text="Upcoming Appointments", font=FONT_HEADER,
                 bg=T["bg"], fg=T["text"]).pack(anchor=tk.W, pady=(4, 4))
        for a in s["upcoming_appointments"]:
            tk.Label(right,
                     text=f"  {a['appointment_date']} {a['appointment_time']}  "
                          f"{a['patient_name']} → {a['doctor_name']}",
                     font=FONT_SMALL, bg=T["bg_card"], fg=T["text"],
                     anchor=tk.W, padx=8, pady=4).pack(fill=tk.X, pady=1)


    def _build_patients(self, parent):
        T = self.tokens
        self._section_label(parent, "🧑‍⚕️  Patient Management")

        sf = tk.Frame(parent, bg=T["bg"])
        sf.pack(fill=tk.X, padx=12, pady=4)
        self.pat_s_name  = self._entry(sf, "Search Name", 18)
        self.pat_s_code  = self._entry(sf, "Patient Code", 12)
        self.pat_s_bg    = self._entry(sf, "Blood Group", 8)
        self.pat_s_amin  = self._entry(sf, "Age Min", 6)
        self.pat_s_amax  = self._entry(sf, "Age Max", 6)
        self._btn(sf, "🔍 Search", self._search_patients)
        self._btn(sf, "✖ Clear", self._refresh_pat,
                  color=self.tokens["bg_secondary"])

        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(fill=tk.X, padx=12, pady=2)
        self._btn(bf, "➕ Add Patient",    self._add_patient)
        self._btn(bf, "✏️  Edit Selected",  self._edit_patient)
        self._btn(bf, "🗑️  Delete Selected", self._delete_patient,
                  color=T["danger"])

        cols = ("ID","Code","Name","Age","Gender","Blood","Phone","Address","Emergency")
        self.pat_tree = self._tree(parent, cols)
        self.pat_tree.column("ID",   width=40)
        self.pat_tree.column("Code", width=80)
        self.pat_tree.column("Age",  width=45)
        self._refresh_pat()

    def _refresh_pat(self, rows=None):
        self.pat_tree.delete(*self.pat_tree.get_children())
        for p in (rows or get_all_patients()):
            self.pat_tree.insert("", tk.END, values=(
                p["id"], p["patient_code"], p["name"], p["age"],
                p["gender"], p["blood_group"], p["phone"],
                p["address"], p["emergency_contact"]
            ))
        self._clear_entry(self.pat_s_name, self.pat_s_code,
                          self.pat_s_bg, self.pat_s_amin, self.pat_s_amax)

    def _search_patients(self):
        try:
            rows = self.us.search_patients(
                name=self.pat_s_name.get() or None,
                patient_code=self.pat_s_code.get() or None,
                blood_group=self.pat_s_bg.get() or None,
                age_min=int(self.pat_s_amin.get()) if self.pat_s_amin.get() else None,
                age_max=int(self.pat_s_amax.get()) if self.pat_s_amax.get() else None,
            )
            self.pat_tree.delete(*self.pat_tree.get_children())
            for p in rows:
                self.pat_tree.insert("", tk.END, values=(
                    p["id"], p["patient_code"], p["name"], p["age"],
                    p["gender"], p["blood_group"], p["phone"],
                    p["address"], p["emergency_contact"]
                ))
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def _add_patient(self):
        dlg = PatientDialog(self, "Add Patient", self.tokens)
        if dlg.result:
            try:
                create_patient(**dlg.result)
                self._refresh_pat()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_patient(self):
        sel = self.pat_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a patient to edit.")
            return
        row = self.pat_tree.item(sel[0])["values"]
        initial = {"name": row[2], "age": row[3], "gender": row[4],
                   "blood_group": row[5], "phone": row[6],
                   "address": row[7], "emergency_contact": row[8]}
        dlg = PatientDialog(self, "Edit Patient", self.tokens, initial)
        if dlg.result:
            try:
                update_patient(int(row[0]), **dlg.result)
                self._refresh_pat()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_patient(self):
        sel = self.pat_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a patient to delete.")
            return
        row = self.pat_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete patient '{row[2]}'?"):
            try:
                delete_patient(int(row[0]))
                self._refresh_pat()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def _build_doctors(self, parent):
        T = self.tokens
        self._section_label(parent, "👨‍⚕️  Doctor Management")

        sf = tk.Frame(parent, bg=T["bg"])
        sf.pack(fill=tk.X, padx=12, pady=4)
        self.doc_s_name  = self._entry(sf, "Search Name", 18)
        self.doc_s_dept  = self._entry(sf, "Department", 14)
        self.doc_s_spec  = self._entry(sf, "Specialization", 14)
        self._btn(sf, "🔍 Search", self._search_doctors)
        self._btn(sf, "✖ Clear", self._refresh_doc,
                  color=self.tokens["bg_secondary"])

        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(fill=tk.X, padx=12, pady=2)
        self._btn(bf, "➕ Add Doctor",    self._add_doctor)
        self._btn(bf, "✏️  Edit Selected",  self._edit_doctor)
        self._btn(bf, "🗑️  Delete Selected", self._delete_doctor,
                  color=T["danger"])

        cols = ("ID","Code","Name","Specialization","Department","Phone","Email")
        self.doc_tree = self._tree(parent, cols)
        self.doc_tree.column("ID",   width=40)
        self.doc_tree.column("Code", width=80)
        self._refresh_doc()

    def _refresh_doc(self, rows=None):
        self.doc_tree.delete(*self.doc_tree.get_children())
        for d in (rows or get_all_doctors()):
            self.doc_tree.insert("", tk.END, values=(
                d["id"], d["doctor_code"], d["name"],
                d["specialization"], d["department"], d["phone"], d["email"]
            ))
        self._clear_entry(self.doc_s_name, self.doc_s_dept, self.doc_s_spec)

    def _search_doctors(self):
        rows = self.us.search_doctors(
            name=self.doc_s_name.get() or None,
            department=self.doc_s_dept.get() or None,
            specialization=self.doc_s_spec.get() or None,
        )
        self.doc_tree.delete(*self.doc_tree.get_children())
        for d in rows:
            self.doc_tree.insert("", tk.END, values=(
                d["id"], d["doctor_code"], d["name"],
                d["specialization"], d["department"], d["phone"], d["email"]
            ))

    def _add_doctor(self):
        dlg = DoctorDialog(self, "Add Doctor", self.tokens)
        if dlg.result:
            try:
                create_doctor(**dlg.result)
                self._refresh_doc()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_doctor(self):
        sel = self.doc_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a doctor to edit.")
            return
        row = self.doc_tree.item(sel[0])["values"]
        initial = {"name": row[2], "specialization": row[3],
                   "department": row[4], "phone": row[5], "email": row[6]}
        dlg = DoctorDialog(self, "Edit Doctor", self.tokens, initial)
        if dlg.result:
            try:
                update_doctor(int(row[0]), **dlg.result)
                self._refresh_doc()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_doctor(self):
        sel = self.doc_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a doctor to delete.")
            return
        row = self.doc_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete doctor '{row[2]}'?"):
            try:
                delete_doctor(int(row[0]))
                self._refresh_doc()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def _build_appointments(self, parent):
        T = self.tokens
        self._section_label(parent, "📅  Appointment Management")

        sf = tk.Frame(parent, bg=T["bg"])
        sf.pack(fill=tk.X, padx=12, pady=4)
        self.appt_s_status = self._entry(sf, "Status", 12)
        self.appt_s_from   = self._entry(sf, "Date From (YYYY-MM-DD)", 14)
        self.appt_s_to     = self._entry(sf, "Date To (YYYY-MM-DD)", 14)
        self._btn(sf, "🔍 Search", self._search_appts)
        self._btn(sf, "✖ Clear", self._refresh_appt,
                  color=self.tokens["bg_secondary"])

        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(fill=tk.X, padx=12, pady=2)
        self._btn(bf, "➕ Add Appointment",  self._add_appt)
        self._btn(bf, "✏️  Edit Selected",    self._edit_appt)
        self._btn(bf, "🗑️  Delete Selected",  self._delete_appt,
                  color=T["danger"])

        cols = ("ID","Patient","Doctor","Date","Time","Status","Notes")
        self.appt_tree = self._tree(parent, cols)
        self.appt_tree.column("ID",     width=40)
        self.appt_tree.column("Date",   width=100)
        self.appt_tree.column("Time",   width=60)
        self.appt_tree.column("Status", width=90)
        self._refresh_appt()

    def _refresh_appt(self, rows=None):
        self.appt_tree.delete(*self.appt_tree.get_children())
        for a in (rows or get_all_appointments()):
            self.appt_tree.insert("", tk.END, values=(
                a["id"], a["patient_name"], a["doctor_name"],
                a["appointment_date"], a["appointment_time"],
                a["status"], a.get("notes", "")
            ))
        self._clear_entry(self.appt_s_status, self.appt_s_from, self.appt_s_to)

    def _search_appts(self):
        rows = self.us.search_appointments(
            status=self.appt_s_status.get() or None,
            date_from=self.appt_s_from.get() or None,
            date_to=self.appt_s_to.get() or None,
        )
        self.appt_tree.delete(*self.appt_tree.get_children())
        for a in rows:
            self.appt_tree.insert("", tk.END, values=(
                a["id"], a["patient_name"], a["doctor_name"],
                a["appointment_date"], a["appointment_time"],
                a["status"], a.get("notes", "")
            ))

    def _add_appt(self):
        dlg = AppointmentDialog(self, "Add Appointment", self.tokens)
        if dlg.result:
            try:
                create_appointment(**dlg.result)
                self._refresh_appt()
                self._refresh_dash()
                self._refresh_cal()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_appt(self):
        sel = self.appt_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment to edit.")
            return
        row = self.appt_tree.item(sel[0])["values"]
        initial = {"appointment_date": row[3], "appointment_time": row[4],
                   "status": row[5], "notes": row[6]}
        dlg = AppointmentDialog(self, "Edit Appointment", self.tokens,
                                initial, edit_mode=True)
        if dlg.result:
            try:
                update_appointment(int(row[0]), **dlg.result)
                self._refresh_appt()
                self._refresh_cal()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_appt(self):
        sel = self.appt_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment to delete.")
            return
        row = self.appt_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete appointment ID {row[0]}?"):
            try:
                delete_appointment(int(row[0]))
                self._refresh_appt()
                self._refresh_dash()
                self._refresh_cal()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def _build_records(self, parent):
        T = self.tokens
        self._section_label(parent, "📋  Medical Records")

        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(fill=tk.X, padx=12, pady=6)
        self._btn(bf, "➕ Add Record",     self._add_record)
        self._btn(bf, "✏️  Edit Selected",   self._edit_record)
        self._btn(bf, "🗑️  Delete Selected", self._delete_record,
                  color=T["danger"])

        cols = ("ID","Patient","Doctor","Diagnosis","Prescription","Date")
        self.rec_tree = self._tree(parent, cols)
        self.rec_tree.column("ID",          width=40)
        self.rec_tree.column("Diagnosis",   width=180)
        self.rec_tree.column("Prescription",width=220)
        self._refresh_rec()

    def _refresh_rec(self, rows=None):
        self.rec_tree.delete(*self.rec_tree.get_children())
        for r in (rows or get_all_medical_records()):
            self.rec_tree.insert("", tk.END, values=(
                r["id"], r["patient_name"], r["doctor_name"],
                r["diagnosis"], r["prescription"], r["record_date"]
            ))

    def _add_record(self):
        dlg = RecordDialog(self, "Add Medical Record", self.tokens)
        if dlg.result:
            try:
                create_medical_record(**dlg.result)
                self._refresh_rec()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_record(self):
        sel = self.rec_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a record to edit.")
            return
        row = self.rec_tree.item(sel[0])["values"]
        initial = {"diagnosis": row[3], "prescription": row[4], "record_date": row[5]}
        dlg = RecordDialog(self, "Edit Medical Record", self.tokens,
                           initial, edit_mode=True)
        if dlg.result:
            try:
                update_medical_record(int(row[0]), **dlg.result)
                self._refresh_rec()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_record(self):
        sel = self.rec_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a record to delete.")
            return
        row = self.rec_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete medical record ID {row[0]}?"):
            try:
                delete_medical_record(int(row[0]))
                self._refresh_rec()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def _build_billing(self, parent):
        T = self.tokens
        self._section_label(parent, "💳  Billing Management")

        sf = tk.Frame(parent, bg=T["bg"])
        sf.pack(fill=tk.X, padx=12, pady=4)
        self.bill_s_status = self._entry(sf, "Status", 12)
        self.bill_s_amin   = self._entry(sf, "Amount Min", 8)
        self.bill_s_amax   = self._entry(sf, "Amount Max", 8)
        self._btn(sf, "🔍 Search", self._search_bills)
        self._btn(sf, "✖ Clear", self._refresh_bill,
                  color=self.tokens["bg_secondary"])

        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(fill=tk.X, padx=12, pady=2)
        self._btn(bf, "➕ Add Bill",        self._add_bill)
        self._btn(bf, "✏️  Edit Selected",   self._edit_bill)
        self._btn(bf, "🗑️  Delete Selected", self._delete_bill_row,
                  color=T["danger"])

        cols = ("ID","Patient","Amount","Status","Date")
        self.bill_tree = self._tree(parent, cols)
        self.bill_tree.column("ID",     width=40)
        self.bill_tree.column("Amount", width=90)
        self.bill_tree.column("Status", width=90)
        self._refresh_bill()

    def _refresh_bill(self, rows=None):
        self.bill_tree.delete(*self.bill_tree.get_children())
        for b in (rows or get_all_bills()):
            self.bill_tree.insert("", tk.END, values=(
                b["id"], b["patient_name"],
                f"Rs. {b['amount']:,.2f}", b["payment_status"], b["bill_date"]
            ))
        self._clear_entry(self.bill_s_status, self.bill_s_amin, self.bill_s_amax)

    def _search_bills(self):
        try:
            rows = self.us.search_bills(
                payment_status=self.bill_s_status.get() or None,
                amount_min=float(self.bill_s_amin.get()) if self.bill_s_amin.get() else None,
                amount_max=float(self.bill_s_amax.get()) if self.bill_s_amax.get() else None,
            )
            self.bill_tree.delete(*self.bill_tree.get_children())
            for b in rows:
                self.bill_tree.insert("", tk.END, values=(
                    b["id"], b["patient_name"],
                    f"Rs. {b['amount']:,.2f}", b["payment_status"], b["bill_date"]
                ))
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def _add_bill(self):
        dlg = BillDialog(self, "Add Bill", self.tokens)
        if dlg.result:
            try:
                create_bill(**dlg.result)
                self._refresh_bill()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_bill(self):
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a bill to edit.")
            return
        row = self.bill_tree.item(sel[0])["values"]
        raw_amount = str(row[2]).replace("Rs. ", "").replace(",", "")
        initial = {"amount": raw_amount, "payment_status": row[3], "bill_date": row[4]}
        dlg = BillDialog(self, "Edit Bill", self.tokens, initial, edit_mode=True)
        if dlg.result:
            try:
                update_bill(int(row[0]), **dlg.result)
                self._refresh_bill()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_bill_row(self):
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a bill to delete.")
            return
        row = self.bill_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete bill ID {row[0]}?"):
            try:
                delete_bill(int(row[0]))
                self._refresh_bill()
                self._refresh_dash()
            except Exception as e:
                messagebox.showerror("Error", str(e))


    def _build_calendar(self, parent):
        T = self.tokens
        self._section_label(parent, "🗓️  Appointment Calendar")

        ctrl = tk.Frame(parent, bg=T["bg"])
        ctrl.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(ctrl, text="Date (YYYY-MM-DD):", font=FONT_SMALL,
                 bg=T["bg"], fg=T["text_muted"]).pack(side=tk.LEFT, padx=4)
        self.cal_date = tk.Entry(ctrl, width=14, font=FONT_SMALL,
                                 bg=T["bg_card"], fg=T["text"],
                                 insertbackground=T["text"], relief=tk.FLAT,
                                 highlightthickness=1,
                                 highlightbackground=T["border"])
        self.cal_date.insert(0, date.today().isoformat())
        self.cal_date.pack(side=tk.LEFT, padx=4)

        self._btn(ctrl, "Day View",   self._cal_day)
        self._btn(ctrl, "Week View",  self._cal_week)
        self._btn(ctrl, "Month View", self._cal_month)

        self.cal_title = tk.Label(parent, text="", font=FONT_HEADER,
                                  bg=T["bg"], fg=T["accent"])
        self.cal_title.pack(anchor=tk.W, padx=16, pady=(4, 0))

        self.cal_info = tk.Label(parent, text="", font=FONT_SMALL,
                                 bg=T["bg"], fg=T["text_muted"])
        self.cal_info.pack(anchor=tk.W, padx=16)

        cols = ("Date","Time","Patient","Doctor","Status","Notes")
        self.cal_tree = self._tree(parent, cols)
        self.cal_tree.column("Date",   width=100)
        self.cal_tree.column("Time",   width=65)
        self.cal_tree.column("Status", width=90)

        self._cal_day()

    def _cal_fill(self, data: dict, view_label: str):
        self.cal_title.configure(text=view_label)
        self.cal_info.configure(
            text=f"Total appointments: {data['total']}"
        )
        self.cal_tree.delete(*self.cal_tree.get_children())
        for a in data["appointments"]:
            self.cal_tree.insert("", tk.END, values=(
                a["appointment_date"], a["appointment_time"],
                a["patient_name"], a["doctor_name"],
                a["status"], a.get("notes", "")
            ))

    def _cal_day(self):
        try:
            d = self.cal_date.get().strip() or date.today().isoformat()
            self._cal_fill(self.us.day_view(d), f"Daily View — {d}")
        except Exception as e:
            messagebox.showerror("Calendar Error", str(e))

    def _cal_week(self):
        try:
            d = self.cal_date.get().strip() or date.today().isoformat()
            data = self.us.week_view(d)
            self._cal_fill(data,
                           f"Weekly View — {data['week_start']} to {data['week_end']}")
        except Exception as e:
            messagebox.showerror("Calendar Error", str(e))

    def _cal_month(self):
        try:
            d = self.cal_date.get().strip() or date.today().isoformat()
            data = self.us.month_view(d)
            self._cal_fill(data,
                           f"Monthly View — {data['month_start']} to {data['month_end']}")
        except Exception as e:
            messagebox.showerror("Calendar Error", str(e))

    def _refresh_cal(self):
        self._cal_day()


    def _clear_entry(self, *entries):
        pass


class _BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, tokens):
        super().__init__(parent)
        self.tokens = tokens
        self.result = None
        self.title(title)
        self.configure(bg=tokens["bg"])
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.wait_window()

    def _field(self, parent, label, default="", width=32):
        T = self.tokens
        f = tk.Frame(parent, bg=T["bg"])
        f.pack(fill=tk.X, padx=20, pady=4)
        tk.Label(f, text=label, font=FONT_SMALL,
                 bg=T["bg"], fg=T["text_muted"], width=20, anchor=tk.W).pack(side=tk.LEFT)
        e = tk.Entry(f, width=width, font=FONT_SMALL,
                     bg=T["bg_card"], fg=T["text"],
                     insertbackground=T["text"], relief=tk.FLAT,
                     highlightthickness=1,
                     highlightbackground=T["border"])
        e.insert(0, str(default))
        e.pack(side=tk.LEFT)
        return e

    def _buttons(self, parent, ok_text="Save"):
        T = self.tokens
        bf = tk.Frame(parent, bg=T["bg"])
        bf.pack(pady=14)
        tk.Button(bf, text=ok_text, font=FONT_BTN, command=self._ok,
                  bg=T["accent"], fg="#ffffff", relief=tk.FLAT,
                  cursor="hand2", padx=16, pady=6,
                  activebackground=T["accent_hover"]).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="Cancel", font=FONT_BTN, command=self.destroy,
                  bg=T["bg_secondary"], fg=T["text"], relief=tk.FLAT,
                  cursor="hand2", padx=16, pady=6).pack(side=tk.LEFT, padx=6)

    def _build(self): pass
    def _ok(self):    pass


class PatientDialog(_BaseDialog):
    def __init__(self, parent, title, tokens, initial=None, **kw):
        self._initial = initial or {}
        super().__init__(parent, title, tokens)

    def _build(self):
        i = self._initial
        tk.Label(self, text=self.title(), font=FONT_HEADER,
                 bg=self.tokens["bg"], fg=self.tokens["accent"]).pack(pady=(16, 4))
        self.e_name  = self._field(self, "Full Name",         i.get("name", ""))
        self.e_age   = self._field(self, "Age",               i.get("age", ""))
        self.e_gen   = self._field(self, "Gender",            i.get("gender", "Male"))
        self.e_bg    = self._field(self, "Blood Group",       i.get("blood_group", "O+"))
        self.e_phone = self._field(self, "Phone",             i.get("phone", ""))
        self.e_addr  = self._field(self, "Address",           i.get("address", ""))
        self.e_emg   = self._field(self, "Emergency Contact", i.get("emergency_contact", ""))
        self._buttons(self)

    def _ok(self):
        try:
            self.result = {
                "name": self.e_name.get().strip(),
                "age": int(self.e_age.get().strip()),
                "gender": self.e_gen.get().strip(),
                "blood_group": self.e_bg.get().strip(),
                "phone": self.e_phone.get().strip(),
                "address": self.e_addr.get().strip(),
                "emergency_contact": self.e_emg.get().strip(),
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.", parent=self)


class DoctorDialog(_BaseDialog):
    def __init__(self, parent, title, tokens, initial=None, **kw):
        self._initial = initial or {}
        super().__init__(parent, title, tokens)

    def _build(self):
        i = self._initial
        tk.Label(self, text=self.title(), font=FONT_HEADER,
                 bg=self.tokens["bg"], fg=self.tokens["accent"]).pack(pady=(16, 4))
        self.e_name  = self._field(self, "Full Name",      i.get("name", ""))
        self.e_spec  = self._field(self, "Specialization", i.get("specialization", ""))
        self.e_dept  = self._field(self, "Department",     i.get("department", ""))
        self.e_phone = self._field(self, "Phone",          i.get("phone", ""))
        self.e_email = self._field(self, "Email",          i.get("email", ""))
        self._buttons(self)

    def _ok(self):
        self.result = {
            "name": self.e_name.get().strip(),
            "specialization": self.e_spec.get().strip(),
            "department": self.e_dept.get().strip(),
            "phone": self.e_phone.get().strip(),
            "email": self.e_email.get().strip(),
        }
        self.destroy()


class AppointmentDialog(_BaseDialog):
    def __init__(self, parent, title, tokens, initial=None, edit_mode=False, **kw):
        self._initial   = initial or {}
        self._edit_mode = edit_mode
        super().__init__(parent, title, tokens)

    def _build(self):
        i = self._initial
        tk.Label(self, text=self.title(), font=FONT_HEADER,
                 bg=self.tokens["bg"], fg=self.tokens["accent"]).pack(pady=(16, 4))
        if not self._edit_mode:
            self.e_pid = self._field(self, "Patient ID", i.get("patient_id", ""))
            self.e_did = self._field(self, "Doctor ID",  i.get("doctor_id", ""))
        self.e_date   = self._field(self, "Date (YYYY-MM-DD)",   i.get("appointment_date", date.today().isoformat()))
        self.e_time   = self._field(self, "Time (HH:MM)",        i.get("appointment_time", "09:00"))
        self.e_status = self._field(self, "Status",              i.get("status", "Scheduled"))
        self.e_notes  = self._field(self, "Notes",               i.get("notes", ""))
        self._buttons(self)

    def _ok(self):
        try:
            if self._edit_mode:
                self.result = {
                    "appointment_date": self.e_date.get().strip(),
                    "appointment_time": self.e_time.get().strip(),
                    "status": self.e_status.get().strip(),
                    "notes": self.e_notes.get().strip(),
                }
            else:
                self.result = {
                    "patient_id": int(self.e_pid.get().strip()),
                    "doctor_id":  int(self.e_did.get().strip()),
                    "appointment_date": self.e_date.get().strip(),
                    "appointment_time": self.e_time.get().strip(),
                    "status": self.e_status.get().strip(),
                    "notes": self.e_notes.get().strip() or None,
                }
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error",
                                 "Patient ID and Doctor ID must be numbers.", parent=self)


class RecordDialog(_BaseDialog):
    def __init__(self, parent, title, tokens, initial=None, edit_mode=False, **kw):
        self._initial   = initial or {}
        self._edit_mode = edit_mode
        super().__init__(parent, title, tokens)

    def _build(self):
        i = self._initial
        tk.Label(self, text=self.title(), font=FONT_HEADER,
                 bg=self.tokens["bg"], fg=self.tokens["accent"]).pack(pady=(16, 4))
        if not self._edit_mode:
            self.e_pid = self._field(self, "Patient ID", i.get("patient_id", ""))
            self.e_did = self._field(self, "Doctor ID",  i.get("doctor_id", ""))
        self.e_diag  = self._field(self, "Diagnosis",    i.get("diagnosis", ""),    width=38)
        self.e_pres  = self._field(self, "Prescription", i.get("prescription", ""), width=38)
        self.e_date  = self._field(self, "Record Date",  i.get("record_date", date.today().isoformat()))
        self._buttons(self)

    def _ok(self):
        try:
            if self._edit_mode:
                self.result = {
                    "diagnosis":    self.e_diag.get().strip(),
                    "prescription": self.e_pres.get().strip(),
                    "record_date":  self.e_date.get().strip(),
                }
            else:
                self.result = {
                    "patient_id":   int(self.e_pid.get().strip()),
                    "doctor_id":    int(self.e_did.get().strip()),
                    "diagnosis":    self.e_diag.get().strip(),
                    "prescription": self.e_pres.get().strip(),
                    "record_date":  self.e_date.get().strip(),
                }
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error",
                                 "Patient ID and Doctor ID must be numbers.", parent=self)


class BillDialog(_BaseDialog):
    def __init__(self, parent, title, tokens, initial=None, edit_mode=False, **kw):
        self._initial   = initial or {}
        self._edit_mode = edit_mode
        super().__init__(parent, title, tokens)

    def _build(self):
        i = self._initial
        tk.Label(self, text=self.title(), font=FONT_HEADER,
                 bg=self.tokens["bg"], fg=self.tokens["accent"]).pack(pady=(16, 4))
        if not self._edit_mode:
            self.e_pid = self._field(self, "Patient ID", i.get("patient_id", ""))
        self.e_amt    = self._field(self, "Amount (Rs.)",    i.get("amount", ""))
        self.e_status = self._field(self, "Payment Status",  i.get("payment_status", "Pending"))
        self.e_date   = self._field(self, "Bill Date",       i.get("bill_date", date.today().isoformat()))
        self._buttons(self)

    def _ok(self):
        try:
            if self._edit_mode:
                self.result = {
                    "amount":         float(self.e_amt.get().strip()),
                    "payment_status": self.e_status.get().strip(),
                    "bill_date":      self.e_date.get().strip(),
                }
            else:
                self.result = {
                    "patient_id":     int(self.e_pid.get().strip()),
                    "amount":         float(self.e_amt.get().strip()),
                    "payment_status": self.e_status.get().strip(),
                    "bill_date":      self.e_date.get().strip(),
                }
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error",
                                 "Patient ID must be integer; Amount must be number.",
                                 parent=self)


if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()

