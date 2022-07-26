import frappe
from frappe.utils import date_diff

def onsubmit(doc, event):
    updateservice(doc)
    if doc.today_odometer_value:
        km = doc.today_odometer_value
        vehicle = frappe.get_doc('Vehicle' , doc.license_plate)
        service = []
        for i in vehicle.service_details_table:
            if event == 'on_submit':
                i.kilometers_after_last_service = (i.kilometers_after_last_service or 0) + km
                if i.kilometers_after_last_service>=i.alert_kilometers and i.frequency == 'Mileage':
                    notification(doc.owner, i.service_item, i.kilometers_after_last_service, doc.name, doc.doctype, "admin@gmail.com")
                    notification(doc.owner, i.service_item, i.kilometers_after_last_service, doc.name, doc.doctype, "agalya@gpy.com")
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
                # k.expense_amount=(k.expense_amount or 0) + (j.expense_amount or 0)
                if k.frequency!='Mileage' and k.frequency!='':
                    k.last_service_date = doc.date
            service.append(k)
        vehicle.service_details_table = service
    vehicle.save()


def notification(owner, service_item, kilometers_after_last_service, name, doctype, user):
    doc=frappe.new_doc('Notification Log')
    doc.update({
    'subject': f'Service Alert for {service_item}',
    'for_user': user,
    'type': 'Alert',
    'document_type': doctype,
    'document_name': name,
    'from_user':owner,
    'email_content': f'{kilometers_after_last_service} KM have been reached after the last service of {service_item}'
    })
    doc.flags.ignore_permissions=True
    doc.save()

def days():
    for vehiclename in frappe.get_all('Vehicle', pluck='name'):
        vehicle = frappe.get_doc('Vehicle' , vehiclename)
        for doc in vehicle.service_details_table:
            if doc.frequency == 'Monthly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//12:
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "admin@gmail.com")
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "agalya@gpy.com")
            if doc.frequency == 'Quarterly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//4:
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "admin@gmail.com")
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "agalya@gpy.com")
            if doc.frequency == 'Half Yearly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365//2:
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "admin@gmail.com")
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "agalya@gpy.com")
            if doc.frequency == 'Yearly':
                if date_diff(frappe.utils.nowdate(), doc.last_service_date) == 365:
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "admin@gmail.com")
                    notification(doc.owner, doc.service_item, doc.kilometers_after_last_service, doc.name, doc.doctype, "agalya@gpy.com")
            

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
    vehicle_log=frappe.new_doc('Vehicle Log')
    vehicle_log.update({
        'license_plate':self.own_vehicle_no,
        'employee':self.employee,
        "date":self.lr_date,
        "odometer":self.return_odometer_value,
        "driver_cost":self.driver_cost,
        "select_purpose":"Goods Supply",
        "delivery_note":self.name
    })
    vehicle_log.flags.ignore_permissions=True
    vehicle_log.save()

def vehicle_log_draft(self, event):
    vehicle_draft=frappe.get_all("Vehicle Log",filters={"docstatus":0,"license_plate":self.license_plate})
    for i in vehicle_draft:
        frappe.db.set_value("Vehicle Log",i.name,"last_odometer",self.odometer)

