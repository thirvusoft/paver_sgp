// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

let data = ganapathy_pavers.monthly_compound_wall_report

data["filters"].push({
    "fieldname": "compound_wall_type",
    "label": __("Compound Wall Type"),
    "fieldtype": "Link",
    "options": "Compound Wall Type",
    "default": "Compound Wall",
    "width": "80",
    "reqd": 1
})

frappe.query_reports["Monthly Compound Wall Production Report"] = data