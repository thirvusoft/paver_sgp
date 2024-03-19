// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

let data = ganapathy_pavers.itemwise_cw_filter

data["filters"].push({
    "fieldname": "compound_wall_type",
    "label": __("Type"),
    "fieldtype": "Link",
    "options": "Compound Wall Type",
    "default": "Compound Wall",
    "width": "80",
    "reqd": 1,
    "on_change": function() {
        let value = frappe.query_report.get_filter_value("compound_wall_type");
        frappe.query_report.page.set_title(`Itemwise Monthly ${value || 'Compound Wall'} Production Report`)
        frappe.query_report.refresh()
    }
})

frappe.query_reports["Itemwise Monthly CW Production Report"] = data

frappe.query_report.get_columns_for_print = function (print_settings, custom_format) {
    let columns = [];

    if (print_settings && print_settings.columns) {
        columns = frappe.query_report.get_visible_columns().filter(column =>
            print_settings.columns.includes(column.fieldname)
        );
    } else {
        columns = frappe.query_report.get_visible_columns();
    }

    return columns;
}
