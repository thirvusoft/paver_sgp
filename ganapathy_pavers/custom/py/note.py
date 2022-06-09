import frappe
from frappe.utils import (add_days,nowdate,)
from frappe.utils import getdate
def note_alert():
    from_date = nowdate()
    to_date = add_days(nowdate(),7)
    day_30 = add_days(nowdate(),30)
    day_30_ = getdate(add_days(nowdate(),30))
    day_15_ = getdate(add_days(nowdate(),15))
    day_15 = add_days(nowdate(),15)
    start_date = getdate(nowdate())
    end_date = getdate(add_days(nowdate(),7))

    doc = frappe.db.sql (""" select name from `tabVehicle`
                             where insurance_expired_date between '{0}' and '{1}' or
                             fc_details_expired_date between '{0}' and '{1}' or
                             road_tax_expired_date between '{0}' and '{1}' or
                             permit_expired_date between '{0}' and '{1}' or
                             pollution_certificate_expired_date between '{0}' and '{1}' or
                             green_tax_expired_date between '{0}' and '{1}' or
                             insurance_expired_date = '{2}' or insurance_expired_date = '{3}' or
                             fc_details_expired_date  = '{2}' or fc_details_expired_date  = '{3}' or
                             road_tax_expired_date  = '{2}' or road_tax_expired_date  = '{3}' or
                             permit_expired_date  = '{2}' or permit_expired_date  = '{3}' or
                             pollution_certificate_expired_date = '{2}' or pollution_certificate_expired_date = '{3}' or
                             green_tax_expired_date  = '{2}' or green_tax_expired_date  = '{3}'
                             """.format(from_date, to_date,day_30,day_15),as_dict=1)
    content = ""
    if(not frappe.db.exists("Note",'Remainder')):
        remainder=frappe.new_doc("Note")
        remainder.title="Remainder"
        remainder.save(ignore_permissions=True)
        frappe.db.commit()
    last_date = []
    notes = frappe.get_doc("Note",'Remainder')
    for d in doc:
        
        title = frappe.get_value("Vehicle",d, "name")
        notes.title = '<b style="color:orange;">Remainder 📢📢📢'
        content+=f'<br>\n\n<b style="color:green;">{title}</b><br>'

        insurance = frappe.get_value("Vehicle",d, "insurance_expired_date")
        
        if (insurance >= start_date and insurance <= end_date or insurance == day_15_ or insurance == day_30_):
            content += f'\nInsurance End on <b style="color:red;">-> {insurance.strftime("%d-%m-%y"+ "<br>")}</b>'
           
            last_date.append(insurance)

        fc = frappe.get_value("Vehicle",d, "fc_details_expired_date")
        if (fc >= start_date and fc <= end_date or fc == day_15_ or fc == day_30_):
            content += f'\nFC End on <b style="color:red;">-> {fc.strftime("%d-%m-%y" + "<br>")}</b>'
            last_date.append(fc)

        road_tax = frappe.get_value("Vehicle",d, "road_tax_expired_date")
        if (road_tax >= start_date and road_tax <= end_date or road_tax == day_15_ or road_tax ==day_30_):
            content += f'\nRoad Tax End on <b style="color:red;">-> {road_tax.strftime("%d-%m-%y" + "<br>")}</b>'
            last_date.append(road_tax)

        permit = frappe.get_value("Vehicle",d, "permit_expired_date")
        if (permit >= start_date and permit <= end_date or permit == day_15_ or permit ==day_30_):
            content += f'\nPermit End on <b style="color:red;">-> {permit.strftime("%d-%m-%y" + "<br>")}</b>'
            last_date.append(permit)

        pollution = frappe.get_value("Vehicle",d, "pollution_certificate_expired_date")
        if (pollution >= start_date and pollution <= end_date or pollution == day_15_ or pollution == day_30_):
            content += f'\nPollution certificate End on <b style="color:red;">-> {pollution.strftime("%d-%m-%y" + "<br>")}</b>'
            last_date.append(pollution)

        green_tax = frappe.get_value("Vehicle",d, "green_tax_expired_date")
        if (green_tax >= start_date and green_tax <= end_date or green_tax == day_15_ or green_tax ==day_30_):
            content += f'\nGreen Tax End on <b style="color:red;">-> {green_tax.strftime("%d-%m-%y" + "<br>")}</b>'
            last_date.append(green_tax)
      
    final_date = max(last_date)
    notes.content = content
    notes.public = 1
    notes.notify_on_login = 1
    # notes.notify_on_every_login = 1
    notes.expire_notification_on = final_date
    notes.save(ignore_permissions=True)
    frappe.db.commit()