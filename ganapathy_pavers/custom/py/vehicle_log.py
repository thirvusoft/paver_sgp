from ganapathy_pavers.custom.py.journal_entry_override import get_workstations
import frappe
import erpnext
from frappe.utils import date_diff

def onsubmit(doc, event):
    updateservice(doc)
    if doc.today_odometer_value:
        km = doc.today_odometer_value
        vehicle = frappe.get_doc('Vehicle' , doc.license_plate)
        service = []
        emailid = frappe.get_single("Vehicle Settings").email_id_for_notification

        for i in vehicle.service_details_table:
            if event == 'on_submit':
                i.kilometers_after_last_service = (i.kilometers_after_last_service or 0) + km
                if i.kilometers_after_last_service>=i.alert_kilometers and i.frequency == 'Mileage':
                    for email in emailid:
                        notification(doc.owner, doc.license_plate, i.service_item, i.kilometers_after_last_service, doc.name, doc.doctype, email.email_id)
            elif event == 'on_cancel':
                i.kilometers_after_last_service = (i.kilometers_after_last_service or 0) - km
            service.append(i)
        vehicle.update({'service_details_table': service})
        vehicle.save()

def updateservice(doc):
    vehicle = frappe.get_doc('Vehicle' , doc.license_plate)
    for j in doc.service_item_table:
        service=[]
        for k in vehicle.service_details_table:
            if j.service_item == k.service_item and j.type == 'Service':
                k.kilometers_after_last_service = 0
                if k.frequency!='Mileage' and k.frequency!='':
                    k.last_service_date = doc.date
            service.append(k)
        vehicle.service_details_table = service
    vehicle.save()


def notification(owner, license_plate, service_item, kilometers_after_last_service, name, doctype, user):
    doc=frappe.new_doc('Notification Log')
    doc.update({
    'subject': f'{license_plate} - Service Alert for {service_item}',
    'for_user': user,
    'send_email': 1,
    'type': 'Alert',
    'document_type': doctype,
    'document_name': name,
    'from_user':owner,
    'email_content': f'{kilometers_after_last_service} KM have been reached for {license_plate} after the last service of {service_item}'
    })
    doc.flags.ignore_permissions=True
    doc.save()

def days():
    for vehiclename in frappe.get_all('Vehicle', pluck='name'):
        vehicle = frappe.get_doc('Vehicle' , vehiclename)
        emailid = frappe.get_single("Vehicle Settings").email_id_for_notification
        for doc in vehicle.service_details_table:
            if doc.frequency == 'Monthly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//12:
                    for email in emailid:
                        notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype,email.email_id)
            if doc.frequency == 'Quarterly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//4:
                    for email in emailid:
                        notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, email.email_id)
            if doc.frequency == 'Half Yearly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//2:
                    for email in emailid:
                        notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype,email.email_id)
            if doc.frequency == 'Yearly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365:
                    for email in emailid:
                        notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, email.email_id)
            

def validate(self, event):
    if(self.select_purpose=='Goods Supply' and self.delivery_note and self.sales_invoice):
        frappe.throw(f"Please don't choose both {frappe.bold('Delivery Note')} and {frappe.bold('Sales Invoice')} under {frappe.bold('Purpose')}")
    if(self.select_purpose=='Raw Material' and self.purchase_invoice and self.purchase_receipt):
        frappe.throw(f"Please don't choose both {frappe.bold('Purchase Receipt')} and {frappe.bold('Purchase Invoice')} under {frappe.bold('Purpose')}")

def update_transport_cost(self, event):
    sw=''
    if(self.select_purpose=='Goods Supply' and self.delivery_note):
        sw=frappe.get_value('Delivery Note', self.delivery_note, 'site_work')
    
    if(self.select_purpose=='Goods Supply' and self.sales_invoice):
        sw=frappe.get_value('Sales Invoice', self.sales_invoice, 'site_work')
    
    if(sw):
        doc=frappe.get_doc('Project', sw)
        cost=0
        if(event=='on_submit'):
            cost=(doc.transporting_cost + self.ts_total_cost or 0)  
        elif(event=='on_cancel'):
            cost=(doc.transporting_cost - self.ts_total_cost or 0)
        doc.update({
            'transporting_cost': cost 
        })
        doc.flags.ignore_mandatory=True
        doc.flags.ignore_permissions=True
        doc.save()

def vehicle_log_creation(self, event):
    if(self.own_vehicle_no):
        vehicle_log=frappe.new_doc('Vehicle Log')
        vehicle_log.update({
            'license_plate':self.own_vehicle_no,
            'employee':self.employee,
            "date":self.lr_date,
            "odometer":self.return_odometer_value,
            "select_purpose":"Goods Supply",
            "delivery_note":self.name
        })
        vehicle_log.flags.ignore_permissions=True
        vehicle_log.save()

def vehicle_log_draft(self, event):
    vehicle_draft=frappe.get_all("Vehicle Log",filters={"docstatus":0,"license_plate":self.license_plate, "select_purpose": ["not in", ["Fuel", "Service"]]})
    for i in vehicle_draft:
        frappe.db.set_value("Vehicle Log",i.name,"last_odometer",self.odometer)

def vehicle_log_mileage(self, event):
    if((frappe.db.get_single_value('Vehicle Settings', 'vehicle_update'))==1):
        if (self.fuel_qty):
                mileage=(self.odometer-self.fuel_odometer_value)/self.fuel_qty
                frappe.db.set_value("Vehicle", self.license_plate, "mileage",mileage)
                frappe.db.set(self, 'mileage', mileage)

def validate_distance(self, event):
    if self.select_purpose=="Service":
        self.odometer=self.last_odometer
    self.today_odometer_value=(self.odometer or 0)-((self.fuel_odometer_value or 0) if self.select_purpose in ["Fuel", "Service"] else (self.last_odometer or 0))

def total_cost(self, event):
    if(self.fuel_qty and self.price):
        self.total_fuel=self.fuel_qty * self.price
    
    self.total_expence=0
    if(self.service_item_table):
        for i in self.service_item_table:
            self.total_expence=(self.total_expence or 0 )+(i.get("expense_amount") or 0)
    
    self.total_expence_maintanence=0
    if(self.maintanence_details):
        self.total_expence_maintanence=0
        for i in self.maintanence_details:
            self.total_expence_maintanence= (self.total_expence_maintanence or 0) +(i.get("expense") or 0)

    self.total_vehicle_costs=(self.total_fuel or 0)+ (self.total_expence or 0)+(self.total_expence_maintanence or 0)


def onsubmit_hours(doc, event):
    updateservice_hours(doc)
    if doc.total_hours_travelled:
        km = doc.total_hours_travelled
        vehicle = frappe.get_doc('Vehicle' , doc.license_plate)
        service = []
        emailid = frappe.get_single("Vehicle Settings").email_id_for_notification
        for i in vehicle.service_details_table:
            if event == 'on_submit':
                i.hours_after_last_service = (i.hours_after_last_service or 0) + km
                if i.hours_after_last_service>=i.alert_hours and i.frequency == 'Hourly':
                    for email in emailid:
                        notification(doc.owner, doc.license_plate, i.service_item, i.hours_after_last_service, doc.name, doc.doctype,email.email_id)
            elif event == 'on_cancel':
                i.hours_after_last_service = (i.hours_after_last_service or 0) - km
            service.append(i)
        vehicle.update({'service_details_table': service})
        vehicle.save()

        
def updateservice_hours(doc):
    vehicle = frappe.get_doc('Vehicle' , doc.license_plate)
    for j in doc.service_item_table:
        service=[]
        for k in vehicle.service_details_table:
            if j.service_item == k.service_item and j.type == 'Service':
                k.hours_after_last_service = 0
                if k.frequency!='Hourly' and k.frequency!='':
                    k.last_service_date = doc.date
            service.append(k)
        vehicle.service_details_table = service
    vehicle.save()
@frappe.whitelist()
def fuel_supplier(name):
    supplier= frappe.get_single("Vehicle Settings").default_fuel_supplier
    return supplier

def update_vehicle_log(self, event=None):
    vl=frappe.get_all("Vehicle Log", {"docstatus": ["!=", 2], "delivery_note": self.name}, pluck="name")
    if vl:
        vl_doc=frappe.get_doc("Vehicle Log", vl[0])
        if vl_doc.docstatus==1:
            frappe.throw(f"Vehicle Log <b><a href='/app/vehicle-log/{vl[0]}'>{vl[0]}</a></b> is submitted.")
        if self.return_odometer_value!=vl_doc.odometer:
            vl_doc.update({
                "odometer": self.return_odometer_value
            })
            vl_doc.save()

def update_delivery_note(self, event=None):
    if self.delivery_note:
        dn=frappe.get_doc("Delivery Note", self.delivery_note)
        if dn.docstatus!=2 and dn.return_odometer_value!=self.odometer:
            dn.update({
                "return_odometer_value": self.odometer
            })
            dn.save("Update")

def supplier_journal_entry(self, event=None):
    if self.select_purpose!="Fuel":
        return
    debit_acc=frappe.db.get_single_value("Vehicle Settings", "fuel_expense")
    if not debit_acc:
        frappe.throw("Please enter <b>Default Expense Account for Fuel Entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    branch=frappe.db.get_single_value("Vehicle Settings", "default_branch")
    if not branch:
        frappe.throw("Please enter <b>Default Branch for Vehicle Expense entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    company=erpnext.get_default_company()
    doc=frappe.new_doc("Journal Entry")
    doc.update({
        "company": company,
        "posting_date": self.date,
        "branch": branch,
        "accounts": update_vehicle_jea_exp(self, [
            {
                "account": get_supplier_credit_acc(self.supplier or frappe.throw(f"Supplier is Mandatory for Fuel Entry in <a href='/app/vehicle-log/{self.name}'>{self.name}</a>"), company),
                "party_type": "Supplier",
                "party": self.supplier or frappe.throw(f"Supplier is Mandatory for Fuel Entry in <a href='/app/vehicle-log/{self.name}'>{self.name}</a>"),
                "credit_in_account_currency": self.total_fuel,
                "branch": branch
            },
            {
                "account": debit_acc,
                "debit_in_account_currency": self.total_fuel,
                "branch": branch
            }
        ]),
        "vehicle_log": self.name
    })
    doc.insert()
    doc.submit()

def get_supplier_credit_acc(supplier, company):
	acc=""
	supplier_doc=frappe.get_doc("Supplier", supplier)
	for row in supplier_doc.accounts:
		if row.company==company:
			acc=row.account
			break
	if not acc:
		supplier_grp_doc=frappe.get_doc("Supplier Group", supplier_doc.supplier_group)
		for row in supplier_grp_doc.accounts:
			if row.company==company:
				acc=row.account
				break
	if not acc:
		acc=frappe.db.get_value("Company", company, "default_payable_account")
	if not acc:
		frappe.throw(f"""Please set <b>Default Payable Account</b> in company <a href="/app/company/{company}"><b>{company}</b></a>""")
	return acc

@frappe.whitelist()
def supplier_fuel_entry_patch():
    created_logs = frappe.get_all("Journal Entry", {"docstatus": 1, "vehicle_log": ["is", "set"]}, pluck="vehicle_log")
    fuel_logs=frappe.get_all("Vehicle Log", {"docstatus": 1, "select_purpose": "Fuel", "total_fuel": [">", 0], "name": ["not in", created_logs]}, pluck="name")
    if not fuel_logs:
        frappe.msgprint(f"""Journal Entry Already created""")
        return
    for log in fuel_logs:
        self=frappe.get_doc("Vehicle Log", log)
        supplier_journal_entry(self)
    frappe.msgprint(f"""Journal Entry created successfully""")

def update_vehicle_jea_exp(self, exp):
    for row in exp:
        row.update({
            "expense_type": self.expense_type,
            "paver": self.paver,
            "compound_wall": self.compound_wall,
            "lego_block": self.lego_block,
            "fencing_post": self.fencing_post,
        })
        if self.get("license_plate"):
            row.update({
                "license_plate": self.get("license_plate")
            })
        row.update({wrk: wrk in [frappe.scrub(row.workstation or "") for row in (self.get("workstations", []) or [])] for wrk in get_workstations()})
    return exp

def service_expenses(self, event=None):
    exp = []
    total_exp=0
    company=erpnext.get_default_company()
    branch=frappe.db.get_single_value("Vehicle Settings", "default_branch")
    if not branch:
        frappe.throw("Please enter <b>Default Branch for Vehicle Expense entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    
    for row in self.service_item_table:
        if row.service_item and row.expense_amount:
            total_exp+=(row.expense_amount or 0)
            exp.append({
                "account": frappe.db.get_value("Service Item", row.service_item, "expense_account") 
                or frappe.throw(f"""Please Enter <b>Expense Account</b> for <a href="/app/service-item/{row.service_item}">{row.service_item}</a>"""),
                "vehicle": self.license_plate,
                "debit_in_account_currency": row.expense_amount,
                "branch": branch
            })
    
    if not exp:
        return
    
    exp = [{
        "account": get_supplier_credit_acc(self.supplier1 or frappe.throw(f"Supplier is Mandatory for Fuel Entry in <a href='/app/vehicle-log/{self.name}'><b>{self.name}</b></a>"), company),
        "party_type": "Supplier",
        "party": self.supplier1 or frappe.throw(f"<b>Supplier</b> is Mandatory for Vehicle Service Expense Entry in <a href='/app/vehicle-log/{self.name}'><b>{self.name}</b></a>"),
        "credit_in_account_currency": total_exp,
        "branch": branch
    }] + exp
    
    doc=frappe.new_doc("Journal Entry")
    doc.update({
        "company": company,
        "posting_date": self.date,
        "branch": branch,
        "accounts": update_vehicle_jea_exp(self, exp),
        "vehicle_log": self.name
    })
    doc.insert()
    doc.submit()