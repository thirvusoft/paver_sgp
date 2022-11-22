# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe 
from frappe import _

def execute(filters=None):
    columns, data = [], [{}]
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data
def get_columns(filters):
    columns = [
        {
            "label": _("Lead Name"),
            "fieldtype": "Data",
            "fieldname": "lead_name",
            "width": 100
        },
        {
            "label": _("Lead Owner"),
            "fieldtype": "Link",
            "fieldname": "lead_owner",
            "options":"User",
            "width": 150
        },
        {
            "label": _("Organization Name"),
            "fieldtype": "Data",
            "fieldname": "company_name",
            "width": 150
        },
        {
            "label": _("Status"),
            "fieldtype": "Select",
            "fieldname": "status",
            "options":"\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact",
            "width": 100
        },
         {
            "label": _("Notes"),
            "fieldtype": "Text Editor",
            "fieldname": "notes",
            "width": 250
        },
        {
            "label": _("Lead Type"),
            "fieldtype": "Select",
            "fieldname": "type",
            "options":"\nPaver\nCompound Wall",
            "width": 100
        },
        {
            "label": _("Source"),
            "fieldtype": "Data",
            "fieldname": "source",
            "width": 100
        },
        {
            "label": _("Reference Name"),
            "fieldtype": "Data",
            "fieldname": "reference_name",
            "width": 100
        }
      ]
    return columns

def get_data(filters):
    lead_t=filters.get('lead_type')
    filter_={'creation':['between',[filters.get('from_date'),filters.get('to_date')]]}
    status_=filters.get('status')
    if lead_t:
        filter_["type"]= lead_t
    if status_:
        filter_['status']= status_
    lead=frappe.db.get_all("Lead", filters=filter_,fields=['lead_name','lead_owner','company_name','status','notes','type', 'source', 'reference_name'])
    return lead
    return lead
