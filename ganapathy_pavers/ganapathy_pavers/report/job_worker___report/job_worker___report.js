// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Worker - Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"site_name",
			"label": __("Site Name"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100"
		},
		{
			"fieldname":"employee",
			"label": __("Job Worker"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100"
		},
		{
			"fieldname": "type",
			"label":  __("Type"),
			"fieldtype": "Select",
			"options": "\nPavers\nCompound Wall"
		},
		{
			"fieldname": "group_site_work",
			"label": __("Group Site Work"),
			"fieldtype": "Check",
			"default": 1
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && (data.status=="Total" || data.job_worker=="Total" || data.bold)) {
			value = `<b>${value}</b>`;

		}
		return value;
	},
};


frappe.query_report.print_report=function print_report(print_settings) {
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

frappe.query_report.pdf_report=function pdf_report(print_settings) {
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