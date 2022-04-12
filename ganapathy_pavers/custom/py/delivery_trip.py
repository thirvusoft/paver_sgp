from time import perf_counter
import frappe
import erpnext
from frappe.model.document import Document
def kilometer(doc,action):
    print("hellllllllllllllllllllllllllllllllllllllllllllllllo",doc.total_distance)
    doc.total_distance = doc.odometer_to_km - doc.odometer_from_km