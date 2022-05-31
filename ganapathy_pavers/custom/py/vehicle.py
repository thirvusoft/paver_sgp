import frappe
from frappe.utils import (add_days,
add_months)


@frappe.whitelist()
def todate(diff, fdate):
    if diff == "Monthly":
         end_date = add_months(fdate, 1)
    elif diff == "Yearly":
        end_date = add_months(fdate, 12)
     
    elif diff == "Quarterly":
        end_date = add_months(fdate, 3)
    else:
        end_date = add_months(fdate, 6)
       
    return end_date


@frappe.whitelist()
def notify(day, month, week, todate):
  doc=frappe.new_doc("Notification")
  doc.update({
        'allow':'TS Subtype',
        'user':user,
        'for_value':subtype

      })
  doc.insert(ignore_permissions=True)
    
