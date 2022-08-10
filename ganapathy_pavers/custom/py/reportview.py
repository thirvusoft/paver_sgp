import frappe
import json

@frappe.whitelist()
def reportview(data):
    try:
        data = json.loads(data)
        if(len(data)>0):
            custom_row = {}
            ts_keys = list(data[0].keys())
            for key in ts_keys:
                for dat in data:
                    if(isinstance(dat[key], int) or isinstance(dat[key], float)):
                        if(key not in custom_row):
                            custom_row[key] = 0
                        custom_row[key] += dat[key]
        return data+[custom_row]
    except:
        pass