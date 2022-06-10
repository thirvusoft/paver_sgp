import frappe
from frappe.utils import (add_days,nowdate,
add_months)


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