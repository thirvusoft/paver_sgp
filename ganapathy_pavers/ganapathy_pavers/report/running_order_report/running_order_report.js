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
            "fieldname": "working_status",
            "label": __("Working Status"),
            "fieldtype": "Select",
            "options": "\nNo Delivery\nDelivery Started & No Laying\nDelivery & Laying Started"
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
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "customer_scope",
            "label": __("Raw Material Customer Scope"),
            "fieldtype": "Check",
        },
        {
            "fieldname": "rate_inclusive",
            "label": __("Raw Material Rate Inclusive"),
            "fieldtype": "Check",
        },
        {
            "fieldname": "include_other_works",
            "label": __("Include Other Works"),
            "fieldtype": "Check",
        },
        {
            "fieldname": "hide_supply_only",
            "label": __("Don't Show Supply Only"),
            "fieldtype": "Check",
            "on_change": function() {
                if (frappe.query_report.get_filter('hide_supply_only').get_value())
                frappe.query_report.get_filter('show_only_supply_only').set_value(!frappe.query_report.get_filter('hide_supply_only').get_value())
                frappe.query_report.refresh()
            }
        },
        {
            "fieldname": "show_only_supply_only",
            "label": __("Show Only Supply Only"),
            "fieldtype": "Check",
            "on_change": function() {
                if (frappe.query_report.get_filter('show_only_supply_only').get_value())
                frappe.query_report.get_filter('hide_supply_only').set_value(!frappe.query_report.get_filter('show_only_supply_only').get_value())
                frappe.query_report.refresh()
            }
        },
    ]
};
