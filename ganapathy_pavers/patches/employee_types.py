import frappe

def execute():
    emp = frappe.db.get_all("Employee", ['name', 'paver', 'compound_wall'])
    for i in emp:
        idx = 1
        if i.paver:
            t = frappe.new_doc('Employee Production Type')
            t.update({
                'type': 'Pavers',
                'parent': i.name,
                'parenttype': 'Employee',
                'parentfield': 'production',
                'idx': idx
            })
            t.save()
            idx += 1
        if i.compound_wall:
            t = frappe.new_doc('Employee Production Type')
            t.update({
                'type': 'Compound Wall',
                'parent': i.name,
                'parenttype': 'Employee',
                'parentfield': 'production',
                'idx': idx
            })
            t.save()

