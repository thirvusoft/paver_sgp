from time import perf_counter
import frappe
import erpnext
from frappe.model.document import Document
def multiply(doc,action):
    print("00000000000000000000000000000000000000000000000000000000000000")
    print(type(doc.per_plate))
    print(type(doc.per_rack))
    doc.per_rack=36*doc.per_plate
    doc.pieces_per_bundle=1000/doc.block_weight