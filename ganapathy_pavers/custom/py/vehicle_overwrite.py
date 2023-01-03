import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from erpnext.hr.doctype.vehicle_log.vehicle_log import VehicleLog
class odometer(VehicleLog):
   def on_submit(self):
		
    if (self.select_purpose =="Fuel" or self.select_purpose =="Service"):
        
        frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", self.last_odometer)
    else:
     
        frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", self.odometer)



