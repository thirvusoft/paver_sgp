import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from erpnext.hr.doctype.vehicle_log.vehicle_log import VehicleLog
class odometer(VehicleLog):
    def validate(self):
        if (self.select_purpose =="Fuel" or self.select_purpose =="Service"):
            if flt(self.odometer) < flt(self.fuel_odometer_value):
                frappe.throw(_("Current Odometer Value should be greater than Last Fuel Odometer Value {0}").format(self.fuel_odometer_value))
        else:
            if flt(self.odometer) < flt(self.last_odometer):
                frappe.throw(_("Current Odometer Value should be greater than Last Odometer Value {0}").format(self.last_odometer))
                        
    def on_submit(self):
		
        if (self.select_purpose =="Fuel" or self.select_purpose =="Service"):
        
            frappe.db.set_value("Vehicle", self.license_plate, "fuel_odometer", self.odometer)
        else:
     
            frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", self.odometer)


    def on_cancel(self):
        if (self.select_purpose =="Fuel" or self.select_purpose =="Service"):
            distance_travelled = self.odometer - self.fuel_odometer_value
            if(distance_travelled > 0):
                updated_odometer_value = int(frappe.db.get_value("Vehicle", self.license_plate, "fuel_odometer")) - distance_travelled
                frappe.db.set_value("Vehicle", self.license_plate, "fuel_odometer", updated_odometer_value)
        else:
            distance_travelled = self.odometer - self.last_odometer
            if(distance_travelled > 0):
                updated_odometer_value = int(frappe.db.get_value("Vehicle", self.license_plate, "last_odometer")) - distance_travelled
                frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", updated_odometer_value)



        
