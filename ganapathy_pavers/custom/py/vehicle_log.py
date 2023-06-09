from ganapathy_pavers.custom.py.journal_entry_override import get_workstations
import frappe
import erpnext
from frappe.utils import date_diff

def onsubmit(doc, event):
    updateservice(doc)
    if doc.today_odometer_value and doc.select_purpose not in ["Fuel", "Service"]:
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
            if j.service_item == k.service_item:
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
    emailid = frappe.get_single("Vehicle Settings").email_id_for_notification
    for vehiclename in frappe.get_all('Vehicle', pluck='name'):
        vehicle = frappe.get_doc('Vehicle' , vehiclename)
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
    if  frappe.db.get_value("Vehicle", self.license_plate, "odometer_depends_on")=="Hours":
        self.total_hours_travelled = self.today_odometer_value

    if(self.select_purpose=='Goods Supply' and self.delivery_note and self.sales_invoice):
        frappe.throw(f"Please don't choose both {frappe.bold('Delivery Note')} and {frappe.bold('Sales Invoice')} under {frappe.bold('Purpose')}")
    if(self.select_purpose=='Raw Material' and self.purchase_invoice and self.purchase_receipt):
        frappe.throw(f"Please don't choose both {frappe.bold('Purchase Receipt')} and {frappe.bold('Purchase Invoice')} under {frappe.bold('Purpose')}")

    if self.select_purpose!="Service":
        self.service_item_table=[]
        self.total_expence=0

    if self.select_purpose!="Fuel":
        self.from_barrel=0
        self.fuel_warehouse=''
        self.fuel_qty=0
        self.price=0
        self.total_fuel=0

    if self.select_purpose!="Adblue":
        self.adblue_item=""
        self.adblue_warehouse=""
        self.adblue_qty=0

    if(self.select_purpose!='Goods Supply'):
        self.delivery_note=""
        if self.select_purpose != "Site Visit":
            self.site_work=""
        self.fastag_charge = 0
        self.payment_to_supplier = 0
        self.fastag_supplier = ""
        self.credit_account = ""
        self.fastag_exp_account = ""
    
    if self.delivery_note:
        self.site_work=frappe.db.get_value("Delivery Note", self.delivery_note, "site_work")
   

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
        frappe.db.set_value("Vehicle Log",i.name,"last_odometer",self.odometer,  update_modified=False)

def vehicle_log_mileage(self, event):
    if((frappe.db.get_single_value('Vehicle Settings', 'vehicle_update'))==1):
        if (self.fuel_qty):
                mileage=(self.odometer-self.fuel_odometer_value)/self.fuel_qty
                frappe.db.set_value("Vehicle", self.license_plate, "mileage",mileage)
                frappe.db.set(self, 'mileage', mileage)

def validate_distance(self, event):
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
            if j.service_item == k.service_item:
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

def update_delivery_note_created(self, event):
    if event=="on_submit" and self.delivery_note and self.select_purpose=="Goods Supply":
        frappe.db.set_value("Delivery Note", self.delivery_note, "vehicle_log_created", 1)
    elif event=="on_cancel" and self.delivery_note and self.select_purpose=="Goods Supply":
        frappe.db.set_value("Delivery Note", self.delivery_note, "vehicle_log_created", 0)

def supplier_journal_entry(self, event=None):
    if not self.select_purpose == "Fuel" or (self.select_purpose == "Fuel" and self.from_barrel):
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
    frappe.msgprint(f"""<b>Journal Entry <a href="/app/journal-entry/{doc.name}">{doc.name}</a></b> for <b>Fuel Expense</b> is created for <b>Vehicle Log <a href="/app/vehicle-log/{self.name}">{self.name}</a></b>""")

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


def update_vehicle_jea_exp(self, exp):
    for row in exp:
        row.update({
            "expense_type": self.expense_type,
            "paver": self.paver,
            "split_equally": self.split_equally,
            "is_shot_blast": self.is_shot_blast,
            "compound_wall": self.compound_wall,
            "lego_block": self.lego_block,
            "fencing_post": self.fencing_post,
        })
        if self.get("license_plate"):
            row.update({
                "vehicle": self.get("license_plate")
            })
        row.update({wrk: wrk in [frappe.scrub(row.workstation or "") for row in (self.get("workstations", []) or [])] for wrk in get_workstations()})
    return exp

def service_expenses(self, event=None):
    return
    if self.select_purpose!="Service":
        return
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
    frappe.msgprint(f"""<b>Journal Entry <a href="/app/journal-entry/{doc.name}">{doc.name}</a></b> for <b>Service Expense</b> is created for <b>Vehicle Log <a href="/app/vehicle-log/{self.name}">{self.name}</a></b>""")

def fastag_expense(self, event=None):
    if self.select_purpose != "Goods Supply" or self.fastag_charge <= 0:
        return
    
    branch=frappe.db.get_single_value("Vehicle Settings", "default_branch")
    if not branch:
        frappe.throw("Please enter <b>Default Branch for Vehicle Expense entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    company=erpnext.get_default_company()

    debit_acc=self.fastag_exp_account
    if not debit_acc:
        debit_acc=frappe.db.get_single_value("Vehicle Settings", "fastag_exp_account")
    if not debit_acc:
        frappe.throw("Please enter <b>Fastag Expense Account</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    
    supplier=""
    credit_acc=""
    if self.payment_to_supplier:
        supplier=self.fastag_supplier
        if not supplier:
            supplier=frappe.db.get_single_value("Vehicle Settings", "fastag_supplier")
        if not supplier:
            frappe.throw(f"""Please enter <b>FASTag Supplier</b>""")

        credit_acc=get_supplier_credit_acc(supplier, company)
    else:
        credit_acc = self.credit_account
        if not credit_acc:
            credit_acc=frappe.db.get_single_value("Vehicle Settings", "credit_account")
        if not credit_acc:
            frappe.throw(f"""Please enter <b>Credit Account</b>""")        
    
    doc=frappe.new_doc("Journal Entry")
    doc.update({
        "company": company,
        "posting_date": self.date,
        "branch": branch,
        "accounts": update_vehicle_jea_exp(self, [
            {
                "account": credit_acc,
                "party_type": "Supplier" if self.payment_to_supplier else "",
                "party": supplier if self.payment_to_supplier else "",
                "credit_in_account_currency": self.fastag_charge,
                "branch": branch
            },
            {
                "account": debit_acc,
                "debit_in_account_currency": self.fastag_charge,
                "branch": branch
            }
        ]),
        "vehicle_log": self.name
    })
    doc.insert()
    doc.submit()
    frappe.msgprint(f"""<b>Journal Entry <a href="/app/journal-entry/{doc.name}">{doc.name}</a></b> for <b>FASTag</b> is created for <b>Vehicle Log <a href="/app/vehicle-log/{self.name}">{self.name}</a></b>""")

def update_fasttag_exp_to_sw(self, event=None):
    if self.select_purpose != "Goods Supply" or self.fastag_charge <= 0:
        return
    
    if self.site_work:
        fastag_exp=frappe.db.get_value("Project", self.site_work, "total_fastag_charges")
        if event == "on_submit":
            current_exp=(fastag_exp or 0) + (self.fastag_charge or 0)
            frappe.db.set_value("Project", self.site_work, "total_fastag_charges", current_exp)
        if event == "on_cancel":
            current_exp=(fastag_exp or 0) - (self.fastag_charge or 0)
            frappe.db.set_value("Project", self.site_work, "total_fastag_charges", current_exp)


def fuel_stock_entry(self, event=None):
    if not self.select_purpose == "Fuel" or (self.select_purpose == "Fuel" and not self.from_barrel):
        return
    
    vehicle_settings=frappe.get_single("Vehicle Settings")
    from_warehouse = self.fuel_warehouse
    if not from_warehouse:
        from_warehouse=frappe.db.get_single_value("Vehicle Settings", "default_fuel_warehouse")
    if not from_warehouse:
        frappe.throw(f"""<b>Fuel Warehouse</b> is required to create <b>Fuel Stock Entry</b> in <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>""")

    vehicle_fuel_type=frappe.db.get_value("Vehicle", self.license_plate, "fuel_type")
    if not vehicle_fuel_type:
        frappe.throw(f"""Please Enter <b>Fuel Type</b> in <b>Vehicle <a href="/app/vehicle/{self.license_plate}">{self.license_plate}</a><b>""")
    
    fuel_item=""
    for row in vehicle_settings.fuel_item_map:
        if row.fuel_type == vehicle_fuel_type:
            fuel_item=row.item_code
            break

    if not fuel_item:
        frappe.throw(f"""<b>Fuel Item</b> is required to create <b>Fuel Stock Entry</b> in <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>. Please Enter the <b>Default Item</b> for Fuel in <a href="/app/vehicle-settings"><b>Vehicle Settings</b></a>""")

    fuel_expense_acc = frappe.db.get_single_value("Vehicle Settings", "fuel_expense")

    if not fuel_expense_acc:
        frappe.throw("Please enter <b>Default Expense Account for Fuel Entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")

    company=erpnext.get_default_company()
    branch=frappe.db.get_single_value("Vehicle Settings", "default_branch")
    if not branch:
        frappe.throw("Please enter <b>Default Branch for Fuel Stock entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    
    doc=frappe.new_doc("Stock Entry")
    doc.update({
        "company": company,
        "branch": branch,
        "stock_entry_type": "Material Issue",
        "vehicle_log": self.name,
        "posting_date": self.date,
        "posting_time": self.time,
        "set_posting_time": bool(self.time),
        "from_warehouse": from_warehouse,
        "items": update_vehicle_jea_exp(self, [{
            "item_code": fuel_item,
            "s_warehouse": from_warehouse,
            "qty": self.fuel_qty,
            "valuation_rate": self.price,
            "basic_rate": self.price,
            "branch": branch,
            "expense_account": fuel_expense_acc,
        }])
    })
    doc.save()
    doc.submit()
    frappe.msgprint(f"""Fuel <b>Stock Entry <a href="/app/stock-entry/{doc.name}">{doc.name}</a></b> Created for <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>""")

def adblue_stock_entry(self, event=None):
    if not self.select_purpose == "Adblue":
        return
    
    vehicle_settings=frappe.get_single("Vehicle Settings")
    from_warehouse = self.adblue_warehouse
    if not from_warehouse:
        from_warehouse=frappe.db.get_single_value("Vehicle Settings", "adblue_warehouse")
    if not from_warehouse:
        frappe.throw(f"""<b>Adblue Warehouse</b> is required to create <b>Adblue Stock Entry</b> in <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>""")

    adblue_item = self.adblue_item

    if not adblue_item:
        adblue_item=vehicle_settings.adblue_item_code

    if not adblue_item:
        frappe.throw(f"""<b>Adblue Item</b> is required to create <b>Adblue Stock Entry</b> in <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>. Please Enter the <b>Default Item</b> for Adblue in <a href="/app/vehicle-settings"><b>Vehicle Settings</b></a>""")

    adblue_expense_acc = frappe.db.get_single_value("Vehicle Settings", "adblue_expense_account")
    if not adblue_expense_acc:
        frappe.throw("Please enter <b>Adblue Expense Account</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")

    company=erpnext.get_default_company()
    branch=frappe.db.get_single_value("Vehicle Settings", "default_branch")
    if not branch:
        frappe.throw("Please enter <b>Default Branch for Stock entry</b> in <a href='/app/vehicle-settings/Vehicle Settings'><b>Vehicle Settings</b></a>")
    
    doc=frappe.new_doc("Stock Entry")
    doc.update({
        "company": company,
        "branch": branch,
        "stock_entry_type": "Material Issue",
        "vehicle_log": self.name,
        "posting_date": self.date,
        "posting_time": self.time,
        "set_posting_time": bool(self.time),
        "from_warehouse": from_warehouse,
        "items": update_vehicle_jea_exp(self, [{
            "item_code": adblue_item,
            "s_warehouse": from_warehouse,
            "qty": self.adblue_qty,
            "branch": branch,
            "expense_account": adblue_expense_acc,
        }])
    })
    doc.save()
    doc.submit()
    frappe.msgprint(f"""Adblue <b>Stock Entry <a href="/app/stock-entry/{doc.name}">{doc.name}</a></b> Created for <a href="/app/vehicle-log/{self.name}"><b>{self.name}</b></a>""")
