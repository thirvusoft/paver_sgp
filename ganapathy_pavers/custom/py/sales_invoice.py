import frappe
import json
import math

def update_customer(self,event):
    cus=self.customer
    for row in self.items:
        so=row.sales_order
        if(so):
            doc=frappe.get_doc('Sales Order', so)
            if(cus!=doc.customer):
                frappe.db.set(doc, "customer", cus)


def validate_stock_qty(doc,event):
    if doc.is_return:
        for i in doc.items:
            if i.delivery_note:
                delivery_stock_qty = frappe.db.get_value("Delivery Note Item", i.dn_detail, "stock_qty") or 0
                returned_qty=delivery_stock_qty - i.stock_qty
                frappe.db.set_value("Delivery Note Item", i.dn_detail, "billed_qty",returned_qty)
                
    for i in doc.items:
        if i.delivery_note:
            delivery_stock_qty = frappe.db.get_value("Delivery Note Item", i.dn_detail, "stock_qty") or 0
            sales_stock_qty=frappe.db.sql(
                                        """
                                        SELECT
                                            sum(stock_qty) as qty from `tabSales Invoice Item`
                                        WHERE
                                            docstatus = 1
                                            and dn_detail= '{dn}'
                                            and name != '{name}'
                                        GROUP BY dn_detail""".format(
                                            dn=i.dn_detail,
                                            name=i.name
                                        ),as_dict=1
	                                )
            if sales_stock_qty:
                sales_stock_qty=sales_stock_qty[0]["qty"] + i.stock_qty
                qty_difference=sales_stock_qty - delivery_stock_qty
                sales_stock_qty=math.ceil(sales_stock_qty)
                delivery_stock_qty=math.ceil(delivery_stock_qty)
                round_qty_difference=sales_stock_qty -delivery_stock_qty
                if round_qty_difference > 1:
                    frappe.throw(("Stcok Qty Differ from Delivery Note Stock Qty {0} in #row {1}").format(qty_difference, i.idx))

def einvoice_validation(self,event):
    accounting=frappe.get_value("Branch",self.branch,"is_accounting")
    if(accounting==1 and not self.get('service_bill') and frappe.db.get_single_value("E Invoice Settings", "enable")):
        if(not self.transporter and not self.vehicle_no and not self.mode_of_transport):
            frappe.throw("Enter the Transport Details")

@frappe.whitelist()
def get_einvoice_no(name="", irn=""):
    erl=frappe.get_all("E Invoice Request Log", {"reference_invoice": f"{name}", "data": ["like", f"""%"Irn": "{irn}",%"""], "response": ["like", '%"success": true,%']}, pluck='response')
    if not erl:
        return
    res=json.loads(erl[0])
    return res.get("result", {}).get("EwbNo")

def update_sales_type(doc, event=None):
    if doc.doctype == 'Sales Invoice':
        doc.db_set("project", doc.site_work)
    doc.reload()
    for gl in frappe.get_all("GL Entry", {"voucher_type": doc.doctype, "voucher_no": doc.name}):
        frappe.db.set_value("GL Entry", gl.name, "type", doc.type)
        if doc.doctype == 'Sales Invoice':
            frappe.db.set_value("GL Entry", gl.name, "project", doc.project)
