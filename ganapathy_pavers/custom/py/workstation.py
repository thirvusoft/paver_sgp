import copy
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.model.utils.rename_field import rename_field
         
wrk_doctypes = ["Journal Entry Account", "Stock Entry Detail", "GL Entry", "Purchase Invoice","Production Expense Table"]

def total_no_salary(doc,action):
    if doc.ts_operators_table:
        total =0
        for i in doc.ts_operators_table:
            total+=(i.ts_operator_wages or 0)
        doc.ts_sum_of_operator_wages = total
        doc.ts_no_of_operator =  len(doc.ts_operators_table)
        
    doc.no_of_total_employees = (doc.no_of_labours or 0) + (doc.ts_no_of_operator or 0)
    doc.sum_of_wages_per_hours = (doc.cal_wages1 or 0) + (doc.ts_sum_of_operator_wages or 0)
        
@frappe.whitelist()
def operator_salary(operator):
    salary = sum(frappe.get_all("Salary Structure Assignment", filters={'employee':operator, 'docstatus': 1}, pluck='base')) / 26
    return salary

def make_custom_field(self, event=None, oldname=None, wrk_dt=wrk_doctypes, insert_after="workstation"):
    if self.used_in_expense_splitup:
        for doctype in wrk_dt:
            meta=frappe.get_meta(doctype)
            create = True
            for row in meta.fields:
                if (row.fieldname == frappe.scrub(self.name) and row.fieldtype == "Check"):
                    create=False
                    continue
            if create:
                if oldname:
                    ia = frappe.get_value("Custom Field", {
                        'dt': doctype,
                        'fieldname': frappe.scrub(oldname)
                    }, 'insert_after')
                    if ia:
                        insert_after=ia
                custom_fields={
                    doctype: [
                            dict(
                                fieldname=frappe.scrub(self.name),
                                label=f"{self.name}",
                                fieldtype="Check",
                                insert_after=insert_after,
                                depends_on="""eval:doc.expense_type=="Manufacturing" """,
                                allow_on_submit=1,
                            ),]
                    }
                create_custom_fields(custom_fields)
    else:
        remove_custom_field(self, wrk_dt=wrk_dt)

def rename_custom_field_workstation(self, event, oldname, newname, merge, wrk_dt=wrk_doctypes, insert_after="workstation"):
    if oldname == newname:
        return
    make_custom_field(self, oldname=oldname, insert_after=insert_after, wrk_dt=wrk_dt)
    for doctype in wrk_dt:
        rename_field(doctype, frappe.scrub(oldname), frappe.scrub(newname))
    if merge:
        copy_custom_field_values(self, oldname, newname, wrk_dt=wrk_dt)
    _self = copy.deepcopy(self)
    _self.name = oldname
    remove_custom_field(_self, event, wrk_dt=wrk_dt)

def copy_custom_field_values(self, oldname, newname, wrk_dt=wrk_doctypes):
    for doctype in wrk_dt:
        frappe.db.sql(f"""
            update `tab{doctype}` 
            set
            `{frappe.scrub(newname)}`=`{frappe.scrub(oldname)}`
            where `{frappe.scrub(oldname)}`
        """)
        frappe.db.sql(f"""
            update `tab{doctype}` 
            set
            `{frappe.scrub(oldname)}`=0
            where `{frappe.scrub(oldname)}`
        """)
    pass

def remove_custom_field(self, event=None, wrk_dt=wrk_doctypes):
    #check field exists
    if not [row for row in frappe.get_meta("GL Entry").fields if row.fieldname==frappe.scrub(self.name)]:
        for i in frappe.get_all("Custom Field", {"dt": ["in", wrk_dt],"fieldname": frappe.scrub(self.name)}, pluck = "name"):
            frappe.delete_doc("Custom Field", i)
        return 
    
    # if field exists
    gl_links = frappe.get_all("GL Entry", filters = {frappe.scrub(self.name): 1}, fields = ["voucher_type", "voucher_no"], group_by="voucher_no, voucher_type")

    if gl_links and not event == "after_rename":
        messgae = "This document is used in Expense entries <ul>"
        for i in gl_links:
            messgae += f"<li><a href='/app/{i.voucher_type}/{i.voucher_no}'>{i.voucher_no}</a></li>"
        
        messgae += "</ul>"

        frappe.throw(messgae)
    
    for i in frappe.get_all("Custom Field", filters={"dt": ["in", wrk_dt],"fieldname": frappe.scrub(self.name)}, fields =[ "name", "insert_after", "dt"]):
        for t in frappe.get_all('Custom Field', filters={'dt': i['dt'], 'insert_after': frappe.scrub(self.name)}, pluck='name'):
            frappe.db.set_value("Custom Field", t, 'insert_after', i['insert_after'])
        frappe.delete_doc("Custom Field", i['name'])
    

