// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Ledger Summary"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book"
		},
		{
			"fieldname":"party",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			on_change: () => {
				var party = frappe.query_report.get_filter_value('party');
				if (party) {
					frappe.db.get_value('Customer', party, ["tax_id", "customer_name"], function(value) {
						frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
						frappe.query_report.set_filter_value('customer_name', value["customer_name"]);
					});
				} else {
					frappe.query_report.set_filter_value('tax_id', "");
					frappe.query_report.set_filter_value('customer_name', "");
				}
			}
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"payment_terms_template",
			"label": __("Payment Terms Template"),
			"fieldtype": "Link",
			"options": "Payment Terms Template"
		},
		{
			"fieldname":"territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory"
		},
		{
			"fieldname":"sales_partner",
			"label": __("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname":"tax_id",
			"label": __("Tax Id"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname":"customer_name",
			"label": __("Customer Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname":"closing_balance_zero",
			"label": __("Don't show zero closing balance"),
			"fieldtype": "Check",
			"default": 1,
			"print_hide": 1
		},
		{
			"fieldname":"closing_balance_opt",
			"label": __("Closing Balance"),
			"fieldtype": "Select",
			"options": "\nGreater than 0\nLess than 0\nEquals 0"
		},
		{
			"fieldname":"sales_type",
			"label": __("Type"),
			"fieldtype": "Link",
			"options": "Types"
		},
		{
			"fieldname": "sales_type_order_and_group",
			"print_hide": 1,
			"label": __("Group and Order by Sales Type"),
			"fieldtype": "Check",
		},
	]
};


frappe.query_report.print_report = function print_report(print_settings) {
	const custom_format = frappe.query_report.report_settings.html_format || null;
	const filters_html = frappe.query_report.get_filters_html_for_print();
	const landscape = print_settings.orientation == 'Landscape';

	frappe.query_report.make_access_log('Print', 'PDF');
	frappe.render_grid({
		template: /*print_settings.columns */!custom_format ? 'print_grid' : custom_format,
		title: __(frappe.query_report.report_name),
		subtitle: filters_html,
		print_settings: print_settings,
		landscape: landscape,
		filters: frappe.query_report.get_filter_values(),
		data: frappe.query_report.get_data_for_print(),
		columns: frappe.query_report.get_columns_for_print(print_settings, custom_format),
		original_data: frappe.query_report.data,
		report: frappe.query_report
	});
}

frappe.query_report.pdf_report = function pdf_report(print_settings) {
	const base_url = frappe.urllib.get_base_url();
	const print_css = frappe.boot.print_css;
	const landscape = print_settings.orientation == 'Landscape';

	const custom_format = frappe.query_report.report_settings.html_format || null;
	const columns = frappe.query_report.get_columns_for_print(print_settings, custom_format);
	const data = frappe.query_report.get_data_for_print();
	const applied_filters = frappe.query_report.get_filter_values();

	const filters_html = frappe.query_report.get_filters_html_for_print();
	const template =
		/*print_settings.columns ||*/ !custom_format ? 'print_grid' : custom_format;
	const content = frappe.render_template(template, {
		title: __(frappe.query_report.report_name),
		subtitle: filters_html,
		filters: applied_filters,
		data: data,
		original_data: frappe.query_report.data,
		columns: columns,
		report: frappe.query_report
	});

	// Render Report in HTML
	const html = frappe.render_template('print_template', {
		title: __(frappe.query_report.report_name),
		content: content,
		base_url: base_url,
		print_css: print_css,
		print_settings: print_settings,
		landscape: landscape,
		columns: columns,
		lang: frappe.boot.lang,
		layout_direction: frappe.utils.is_rtl() ? "rtl" : "ltr"
	});

	frappe.render_pdf(html, print_settings);
}
