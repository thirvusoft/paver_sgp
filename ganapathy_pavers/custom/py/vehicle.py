import frappe
from frappe.utils import add_months, add_days, nowdate


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
    vehicle_name=self.name
    list1=[]
    if self.vehicle_common_groups:
    
        for i in self.vehicle_common_groups:
            list1.append(i.__dict__)
       
        expense_account=frappe.db.get_values("Expense Account Common Groups",{"parent":"Expense Accounts"},"*",as_dict=True)
        if expense_account:
            frappe.db.sql("""delete from `tabExpense Account Common Groups` where parent="Expense Accounts" and vehicle='{0}'""".format(self.name))
            
            doc=frappe.get_doc("Expense Accounts")
            for accounts in list1:
                doc.append("expense_account_common_groups",{
                    "paver_account":accounts["paver_account"],
                    "cw_account":accounts["cw_account"],
                    "lg_Account":accounts["lg_account"],
                    "fp_account":accounts["fp_account"],
                    "monthly_cost":accounts["monthly_cost"],
                    "vehicle":accounts["vehicle"]
                })
               
                doc.save()
                doc.reload()
        else:
            print("hhhhhhhhhh")
            doc=frappe.get_doc("Expense Accounts")
            for accounts in list1:
                doc.append("expense_account_common_groups",{
                    "paver_account":accounts["paver_account"],
                    "cw_account":accounts["cw_account"],
                    "lg_Account":accounts["lg_account"],
                    "fp_account":accounts["fp_account"],
                    "monthly_cost":accounts["monthly_cost"],
                    "vehicle":accounts["vehicle"]
                })
                doc.save()
               


       
          


        


  
