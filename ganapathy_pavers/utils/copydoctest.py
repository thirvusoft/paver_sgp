import frappe
from frappe.core.doctype.server_script.server_script_utils import run_server_script_for_doc_event
from frappe.integrations.doctype.webhook import run_webhooks
from frappe.model.document import Document

primesite = "prime" #"sgpprime.thirvusoft.co.in"
mainsite = "tsgp" #"sgp.thirvusoft.co.in"


def set_user_and_timestamp(self):
    frappe.flags.currently_saving.append((self.doctype, self.name))

"""run standard triggers, plus those in hooks"""
def run_method(self, method, *args, **kwargs):
    def fn(self, *args, **kwargs):
        method_object = getattr(self, method, None)

        # Cannot have a field with same name as method
        # If method found in __dict__, expect it to be callable
        if method in self.__dict__ or callable(method_object):
            return method_object(*args, **kwargs)

    fn.__name__ = str(method)
    out = Document.hook(fn)(self, *args, **kwargs)

    self.run_notifications(method)
    run_webhooks(self, method)
    run_server_script_for_doc_event(self, method)

    return out


def delete(doctype):
    x, s, f=0, 0, 0
    for i in frappe.get_all(doctype):
        print(x)
        x+=1
        # try:
        doc=frappe.get_doc(doctype, i.name)
        if doc.docstatus == 1:
            doc.cancel()
        doc.delete()
        s+=1
        # except:
        #     f+=1
        #     pass
        
        print('DELETE', x, s, f)

        
def copy(doctype, empty_fields = {}, filters={}):
    docs=[]
    prime_docs = []
    with frappe.init_site(primesite):
        frappe.connect(site=primesite)
        frappe.session.siteName = "sgpprime"
        prime_docs = frappe.get_all(doctype, pluck="name")
    print("PRIME DOCS", len(prime_docs))


    with frappe.init_site(mainsite):
        frappe.connect(site=mainsite)
        filters={
            "name": ["not in", prime_docs],
            "name": "MAT-LCV-2023-01451",
            "posting_date": [">=", "2023-04-01"], 
            "branch": "SG 1", 
            "docstatus": 1
        }

        if doctype == "Landed Cost Voucher":
            filters={
                "name": ["not in", prime_docs],
                "posting_date": [">=", "2023-04-01"], 
                # "branch": "SG 1", 
                "docstatus": 1
            }

        for i in frappe.get_all(doctype, filters, pluck="name"):
            docs.append(frappe.get_doc(doctype, i))
    total = len(docs)
    print("TOTAL", total)
    s, f = 0, 0

    with frappe.init_site(primesite):
        frappe.connect(site=primesite)

        frappe.session.siteName = "sgpprime"
        print()
        for doc in docs:
            print(total, s+f, s, f, doc.name)

            for i in empty_fields:
                doc.__setattr__(i, empty_fields[i])
            doc.amended_from = ""
            doc.run_method = lambda *a, **r:0
            doc.set_user_and_timestamp = lambda *a, **r: set_user_and_timestamp(doc)
            doc.flags.name_set = True
            doc.insert()
            run_method(doc, "before_submit")
            run_method(doc, "on_submit")
            frappe.db.commit()
            s+=1
            # except:
            #     pass
            #     f+=1
            
            
def lcv_create():
    with frappe.init_site(primesite):
        frappe.connect(site=primesite)
        frappe.session.siteName = "sgpprime"
        for i in frappe.db.get_all("Purchase Invoice"):
            frappe.db.set_value("Purchase Invoice", i.name, 'update_stock', 1)
        
        for i in frappe.db.get_all("Item"):
            frappe.db.set_value("Item", i.name, 'is_stock_item', 1)

        frappe.db.commit()

        print(len(frappe.db.get_all("Item")), len(frappe.db.get_all("Item", {'docstatus': 1})))


    copy(doctype="Landed Cost Voucher", empty_fields = {}, filters={})

    with frappe.init_site(primesite):
        frappe.connect(site=primesite)
        frappe.session.siteName = "sgpprime"
        for i in frappe.db.get_all("Purchase Invoice"):
            frappe.db.set_value("Purchase Invoice", i.name, 'update_stock', 0)
        
        for i in frappe.db.get_all("Item"):
            frappe.db.set_value("Item", i.name, 'is_stock_item', 0)
        
        frappe.db.commit()
    

def pi():
    delete("Purchase Invoice")
    copy("Purchase Invoice", {'update_stock': 0})