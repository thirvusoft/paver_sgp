//apps/erpnext/erpnext/accounts/report/item_wise_purchase_register/item_wise_purchase_register.js
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Item-wise Purchase Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"mode_of_payment",
			"label": __("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment"
		},
		{
			"label": __("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return {
					filters: {
						"company": frappe.query_report.get_filter_value("company")
					}
				}
			}
		},
		{
			"label": __("Group By"),
			"fieldname": "group_by",
			"fieldtype": "Select",
			"options": ["Supplier", "Item Group", "Item", "Invoice"]
		},
		{
			"label": __("Type"),
			"fieldname": "type",
			"fieldtype": "Select",
			"options": ["", "Pavers", "Compound Wall", "Vehicle", "Site", "Others"]
		} //customized
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	}
}


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
