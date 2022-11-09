import frappe

def execute():
    update_check_box("Sales Order")


def update_check_box(doctype):
    uncheck_branch = frappe.get_all("Branch", {'is_accounting': 0}, pluck="name")
    docs=frappe.get_all(doctype, {'branch': ['in', uncheck_branch], 'docstatus': ['!=', '2']}, pluck="name")
    for doc in docs:
        _doc=frappe.get_doc(doctype, doc)
        for row in _doc.items:
            row.unacc=1
        _doc.save('update')