from math import remainder
import frappe
from frappe.utils import (add_days,
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
    email=frappe.get_all("Email Account",filters={'enable_outgoing':1},pluck='name')
    email=email.email_id
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
            'sender':email,
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
                'sender':email,
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
                'sender':email,
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
                'sender':email,
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
                'sender':email,
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
                'sender':email,
            })
        
            doc.insert(ignore_permissions=True)
            row(lic)
            return end_date
    
def row(lic):
    doc=frappe.get_doc("Notification",lic)
    row = doc.append('recipients', {})
    row.receiver_by_role = "Fleet Manager"
    doc.save()


