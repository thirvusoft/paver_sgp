import frappe
from frappe.utils import add_months, add_days, nowdate,get_first_day,get_last_day


@frappe.whitelist()
def todate(diff, fdate, duaration, lic, main):
    if diff == "Monthly":
         end_date = add_months(fdate, 1)
    elif diff == "Yearly":
        end_date = add_months(fdate, 12)
     
    elif diff == "Quarterly":
        end_date = add_months(fdate, 3)
    else:
        end_date = add_months(fdate, 6)
       
    return notify(end_date, duaration, lic, main)


@frappe.whitelist()
def notify(end_date, duaration, lic, main):
    email=frappe.get_all("Email Account",filters={'enable_outgoing':1},fields=['name','email_id'])
    email=email[0].email_id
    if main == "Insurance":   
        doc=frappe.new_doc("Notification")
        lic = lic+'-'+'Insurance'
        doc.update({
            'doctype':'Notification',
            '__newname':lic,
            'channel':'Email',
            'subject':lic,
            'document_type':'Vehicle',
            'event':'Days Before',
            'date_changed':'end_date',
            'days_in_advance':duaration,
            'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
            'send_to_all_assignees':True,
            'send_system_notification':True
        })

        doc.insert(ignore_permissions=True)
        row(lic)
        return end_date
    if main == "FC Details":
            doc=frappe.new_doc("Notification")
            lic=lic+'-'+'FC Details'
            doc.update({
                'doctype':'Notification',
                '__newname':lic,
                'channel':'Email',
                'subject':lic,
                'document_type':'Vehicle',
                'event':'Days Before',
                'date_changed':'end_date',
                'days_in_advance':duaration,
                'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
                'send_to_all_assignees':True,
                'send_system_notification':True
            })
        
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date

    if main == "Road Tax":
            doc=frappe.new_doc("Notification")
            lic=lic+'-'+'Road Tax'
            doc.update({
                'doctype':'Notification',
                '__newname':lic,
                'channel':'Email',
                'subject':lic,
                'document_type':'Vehicle',
                'event':'Days Before',
                'date_changed':'end_date',
                'days_in_advance':duaration,
                'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
                'send_to_all_assignees':True,
                'send_system_notification':True
            })
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date
    if main == "Permit":
            doc=frappe.new_doc("Notification")
            lic=lic+'-'+'Permit'
            doc.update({
                'doctype':'Notification',
                '__newname':lic,
                'channel':'Email',
                'subject':lic,
                'document_type':'Vehicle',
                'event':'Days Before',
                'date_changed':'end_date',
                'days_in_advance':duaration,
                'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
                'send_to_all_assignees':True,
                'send_system_notification':True
            })
        
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date
    if main == "Pollution Certificate":
            doc=frappe.new_doc("Notification")
            lic=lic+'-'+'Pollution Certificate"'
            doc.update({
                'doctype':'Notification',
                '__newname':lic,
                'channel':'Email',
                'subject':lic,
                'document_type':'Vehicle',
                'event':'Days Before',
                'date_changed':'end_date',
                'days_in_advance':duaration,
                'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
                'send_to_all_assignees':True,
                'send_system_notification':True
            })
        
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date
    if main == "Green Tax":
            doc=frappe.new_doc("Notification")
            lic=lic+'-'+'Green Tax'
            doc.update({
                'doctype':'Notification',
                '__newname':lic,
                'channel':'Email',
                'subject':lic,
                'document_type':'Vehicle',
                'event':'Days Before',
                'date_changed':'end_date',
                'days_in_advance':duaration,
                'message': 'Vehicle'+' '+lic+' '+'Remainder'+' '+'Alert'+' '+'(End Date)'+' - '+end_date,
                'send_to_all_assignees':True,
                'send_system_notification':True
            })
        
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date
    
def row(lic):
    doc=frappe.get_doc("Notification",lic)
    row = doc.append('recipients', {})
    row.receiver_by_role = "Fleet Manager"
    doc.save()

def reference_date(doc,action):
    for data in doc.maintanence_details_:
        if (data.maintenance == "Insurance"):
            if(data.to_date != ""):
                doc.insurance_expired_date = data.to_date
            
        if (data.maintenance == "FC Details"):
            if(data.to_date != ""):
                doc.fc_details_expired_date = data.to_date
                
        if (data.maintenance == "Road Tax"):
            if(data.to_date != ""):
                doc.road_tax_expired_date = data.to_date

        if (data.maintenance == "Permit"):
            if(data.to_date != ""):
                doc.permit_expired_date = data.to_date

        if (data.maintenance == "Pollution Certificate"):
            if(data.to_date != ""):
                doc.pollution_certificate_expired_date = data.to_date

        if (data.maintenance == "Green Tax"):
            if(data.to_date != ""):
                doc.green_tax_expired_date = data.to_date



def notification(remainder_type, owner, license_plate, maintenance_item, doctype):
    emailid = frappe.get_single("Vehicle Settings").email_id_for_notification
    for email in emailid:
        doc=frappe.new_doc('Notification Log')
        doc.update({
        'subject': f'{license_plate} - Maintenance Alert for {maintenance_item}',
        'for_user': email.email_id,
        'send_email': 1,
        'type': 'Alert',
        'document_type': doctype,
        'document_name': license_plate,
        'from_user':owner,
        'email_content': f'A {remainder_type} Remainder for a Maintenance item: {maintenance_item} in Vehicle: {license_plate}'
        })
        doc.flags.ignore_permissions=True
        doc.save()


def vehicle_maintenance_notification():
    vehicle = frappe.get_all("Maintenance Details", {'parenttype': 'Vehicle'}, pluck='name')
    for doc in vehicle:
        doc=frappe.get_doc('Maintenance Details', doc)
        if (doc.to_date):
            if(doc.month_before and str(doc.to_date) == add_months(nowdate(), 1)):
                notification("Month Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')
            if(doc.week_before and str(doc.to_date) == add_days(nowdate(), 7)):
                notification("Week Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')
            if(doc.day_before and str(doc.to_date) == add_days(nowdate(), 1)):
                notification("Day Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')



def vehicle_common_groups(self,event):
    for i in self.vehicle_common_groups:
        i.vehicle = self.name
    frappe.db.sql("""delete from `tabVehicle Expense Account` where parent="Expense Accounts" and vehicle='{0}'""".format(self.name))
    doc=frappe.get_doc("Expense Accounts")
    doc.update({
        "vehicle_expense_accounts": doc.vehicle_expense_accounts + [
            {
                "expense_account": child_doc.expense_account,
                "vehicle":child_doc.vehicle,
                "monthly_cost":child_doc.monthly_cost
            } for child_doc in self.vehicle_common_groups]
    })
    doc.run_method=lambda *args, **kwargs: 0
    doc.save()

@frappe.whitelist()
def fuel_and_tyers_cost(date):
    tyre_cost_details=[]
    fuel_cost_details=[]
    vehicle_list=frappe.get_all("Vehicle",pluck="name")
    month_start_date = get_first_day(date)
    month_end_date = get_last_day(date)
    for vehicle in vehicle_list:
        fuel_cost_details.append(frappe.db.sql("""
            select 
                sum(vl.total_fuel) as total,
                v.fuel_account as account,
                v.license_plate as vehicle 
            from `tabVehicle Log` vl,`tabVehicle` v 
            where 
                vl.license_plate='{0}' 
                and v.name='{0}' 
                and vl.select_purpose="Fuel" 
                and vl.date between '{1}' and '{2}' 
                and vl.docstatus=1 
            group by vl.license_plate
        """.format(vehicle, month_start_date, month_end_date), as_dict=1)) 
        tyre_cost_details+=frappe.db.sql("""
            select 
                (sum(vl.today_odometer_value)/v.tyer_cost) as total,
                vl.license_plate as vehicle,
                v.tyer_account as account  
            from `tabVehicle Log` vl,`tabVehicle` v 
            where 
                vl.license_plate='{0}' 
                and v.name='{0}' 
                and vl.select_purpose not in ("Fuel","Service") 
                and vl.date between '{1}' and '{2}' 
                and vl.docstatus=1 
            group by vl.license_plate
        """.format(vehicle,month_start_date,month_end_date),as_dict=1)
    cost=frappe.get_single("Expense Accounts")
    res1=[]
    for i in cost.vehicle_expense_accounts:
        res={}
        res["account"]=i.expense_account 
        res["vehicle"]=i.vehicle
        res["total"]=i.monthly_cost
        res1.append(res)
    return res1+tyre_cost_details+fuel_cost_details
