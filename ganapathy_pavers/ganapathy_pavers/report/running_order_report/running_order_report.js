// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Running Order Report"] = {
    "filters": [
        {
            "fieldname": "site_name",
            "label": __("Site Name"),
            "fieldtype": "Link",
            "options": "Project",
            "get_query": function () {
                var customer = frappe.query_report.get_filter_value('customer');
                if (!customer) {
                    return {}
                }
                return {
                    filters: {
                        "customer": customer
                    }
                };
            },
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
        },
        {
            "fieldname": "type",
            "label": __("Type"),
            "fieldtype": "Select",
            "default": "Pavers",
            "options": "Pavers\nCompound Wall"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            'options': frappe.get_meta('Project').fields.filter(df => df.fieldname === 'status')[0].options,
            'default': frappe.get_meta('Project').fields.filter(df => df.fieldname === 'status')[0].options.includes('Open')?"Open":""
        },
        {
            "fieldname": "include_other_works",
            "label": __("Include Other Works"),
            "fieldtype": "Check",
        },
    ]
};
