import frappe
from frappe.utils import get_date_str, format_date, cint



def autoname(self, event=None):
    try:
        date = None
        if(self.reference_doctype == "Stock Entry" and self.reference_name):
            se_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
            if(se_doc.usb):
                usb_date = frappe.get_value("Material Manufacturing", se_doc.usb, 'from_time_rack') or frappe.throw(f"Plaese Enter Unmolding Date in {frappe.bold(frappe.utils.csvutils.getlink('Material Manufacturing', se_doc.usb))}")
                if(usb_date):
                    date=get_date_str(usb_date)
            elif(se_doc.cw_usb):
                cw_usb_date = frappe.get_value("CW Manufacturing", se_doc.cw_usb, 'unmolding_date') or frappe.throw(f"Plaese Enter Unmolding Date in {frappe.bold(frappe.utils.csvutils.getlink('CW Manufacturing', se_doc.cw_usb))}")
                if(cw_usb_date):
                    date=str(cw_usb_date)
            else:
                if(se_doc.posting_date):
                    date = get_date_str(se_doc.posting_date)
        if not date:
            date = frappe.utils.nowdate()
        date = format_date(date, 'dd-mm-yyyy')


        naming_series = "SGP.-"
        doc = frappe.db.sql (f""" select * from tabSeries where name = "{naming_series}" """)
        if len(doc)==0:
            frappe.db.sql(f""" INSERT INTO tabSeries VALUES ("{naming_series}",0) """)
        series = frappe.db.sql (f""" select current from tabSeries where name = "{naming_series}" """)
        if(series and series[0]):
            series = series[0][0]

        frappe.db.sql("update `tabSeries` set current = %s where name = %s",
                    (cint(series)+1, naming_series))
        series = frappe.db.sql (f""" select current from tabSeries where name = "{naming_series}" """)
        if(series and series[0]):
            series = series[0][0]
        name = f"{date}-{('0'*(2-len(str(series)))) if(len(str(series))<2) else ''}{series}"
        if(not frappe.db.exists("Batch", name)):
            self.name = name
            if(not self.batch_id):
                self.batch_id = name
    except:
        pass

def update_series(self, event=None):
    if(frappe.get_all('Batch') and frappe.get_last_doc('Batch').name==self.name):
        naming_series = "SGP.-"
        series = frappe.db.sql (f""" select current from tabSeries where name = "{naming_series}" """)
        if(series and series[0]):
            series = series[0][0]
            frappe.db.sql("update `tabSeries` set current = %s where name = %s",
                    (cint(series)-1, naming_series))
