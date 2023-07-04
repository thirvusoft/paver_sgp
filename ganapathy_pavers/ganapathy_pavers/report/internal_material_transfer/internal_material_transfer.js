// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt
/* eslint-disable */

var vehicles = [], drivers = [], operators = [];

let refresh_fn = frappe.query_report.refresh
frappe.query_report.refresh = async (...args) => {
	vehicles = await frappe.db.get_list("Stock Entry", {
		limit: 0,
		filters: {
			docstatus: 1,
			is_internal_stock_transfer: 1,
			stock_entry_type: 'Material Transfer'
		},
		fields: ['vehicle'],
		pluck: 'vehicle'
	})

	drivers = await frappe.db.get_list("Stock Entry", {
		limit: 0,
		filters: {
			docstatus: 1,
			is_internal_stock_transfer: 1,
			stock_entry_type: 'Material Transfer'
		},
		fields: ['driver'],
		pluck: 'driver'
	})

	operators = await frappe.db.get_list("Stock Entry", {
		limit: 0,
		filters: {
			docstatus: 1,
			is_internal_stock_transfer: 1,
			stock_entry_type: 'Material Transfer'
		},
		fields: ['operator'],
		pluck: 'operator'
	})
	refresh_fn.call(frappe.query_report, ...args)
}


frappe.query_reports["Internal Material Transfer"] = {
	filters: [
		{
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7)
		},
		{
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -1)
		},
		{
			fieldname: 'item_code',
			label: __('Item'),
			fieldtype: 'MultiSelectList',
			get_data: async function (txt) {
				let filters = [
					['Stock Entry', 'docstatus', '=', '1'],
					['Stock Entry', 'stock_entry_type', '=', 'Material Transfer'],
					['Stock Entry', 'is_internal_stock_transfer', '=', '1']
				];

				if (frappe.query_report.get_filter_value('from_date')) {
					filters.push(['Stock Entry', 'posting_date', '>=', frappe.query_report.get_filter_value('from_date')])
				}
				if (frappe.query_report.get_filter_value('to_date')) {
					filters.push(['Stock Entry', 'posting_date', '<=', frappe.query_report.get_filter_value('to_date')])
				}
				if (frappe.query_report.get_filter_value('s_warehouse')?.length) {
					filters.push(['Stock Entry Detail', 's_warehouse', 'in', frappe.query_report.get_filter_value('s_warehouse')])
				}
				if (frappe.query_report.get_filter_value('t_warehouse')?.length) {
					filters.push(['Stock Entry Detail', 't_warehouse', 'in', frappe.query_report.get_filter_value('t_warehouse')])
				}
				if (frappe.query_report.get_filter_value('vehicle')) {
					filters.push(['Stock Entry', 'vehicle', '=', frappe.query_report.get_filter_value('vehicle')])
				}
				if (frappe.query_report.get_filter_value('driver')) {
					filters.push(['Stock Entry', 'driver', '=', frappe.query_report.get_filter_value('driver')])
				}
				if (frappe.query_report.get_filter_value('operator')) {
					filters.push(['Stock Entry', 'operator', '=', frappe.query_report.get_filter_value('operator')])
				}

				return frappe.db.get_list("Stock Entry", {
					filters: filters,
					group_by: "item_code",
					fields: ['`tabStock Entry Detail`.item_code as value', '`tabStock Entry Detail`.item_name as description'],
					limit: 0
				});
			}
		},
		{
			fieldname: 's_warehouse',
			label: __('From Warehouse'),
			fieldtype: 'MultiSelectList',
			get_data: function (txt) {
				let filters = [
					['Stock Entry', 'docstatus', '=', '1'],
					['Stock Entry', 'stock_entry_type', '=', 'Material Transfer'],
					['Stock Entry', 'is_internal_stock_transfer', '=', '1']
				];

				if (frappe.query_report.get_filter_value('from_date')) {
					filters.push(['Stock Entry', 'posting_date', '>=', frappe.query_report.get_filter_value('from_date')])
				}
				if (frappe.query_report.get_filter_value('to_date')) {
					filters.push(['Stock Entry', 'posting_date', '<=', frappe.query_report.get_filter_value('to_date')])
				}
				if (frappe.query_report.get_filter_value('item_code')?.length) {
					filters.push(['Stock Entry Detail', 'item_code', 'in', frappe.query_report.get_filter_value('item_code')])
				}
				if (frappe.query_report.get_filter_value('t_warehouse')?.length) {
					filters.push(['Stock Entry Detail', 't_warehouse', 'in', frappe.query_report.get_filter_value('t_warehouse')])
				}
				if (frappe.query_report.get_filter_value('vehicle')) {
					filters.push(['Stock Entry', 'vehicle', '=', frappe.query_report.get_filter_value('vehicle')])
				}
				if (frappe.query_report.get_filter_value('driver')) {
					filters.push(['Stock Entry', 'driver', '=', frappe.query_report.get_filter_value('driver')])
				}
				if (frappe.query_report.get_filter_value('operator')) {
					filters.push(['Stock Entry', 'operator', '=', frappe.query_report.get_filter_value('operator')])
				}

				return frappe.db.get_list("Stock Entry", {
					filters: filters,
					group_by: "s_warehouse",
					fields: ['`tabStock Entry Detail`.s_warehouse as value', '`tabStock Entry Detail`.s_warehouse as description'],
					limit: 0
				});
			}
		},
		{
			fieldname: 't_warehouse',
			label: __('To Warehouse'),
			fieldtype: 'MultiSelectList',
			get_data: function (txt) {
				let filters = [
					['Stock Entry', 'docstatus', '=', '1'],
					['Stock Entry', 'stock_entry_type', '=', 'Material Transfer'],
					['Stock Entry', 'is_internal_stock_transfer', '=', '1']
				];

				if (frappe.query_report.get_filter_value('from_date')) {
					filters.push(['Stock Entry', 'posting_date', '>=', frappe.query_report.get_filter_value('from_date')])
				}
				if (frappe.query_report.get_filter_value('to_date')) {
					filters.push(['Stock Entry', 'posting_date', '<=', frappe.query_report.get_filter_value('to_date')])
				}
				if (frappe.query_report.get_filter_value('item_code')?.length) {
					filters.push(['Stock Entry Detail', 'item_code', 'in', frappe.query_report.get_filter_value('item_code')])
				}
				if (frappe.query_report.get_filter_value('s_warehouse')?.length) {
					filters.push(['Stock Entry Detail', 's_warehouse', 'in', frappe.query_report.get_filter_value('s_warehouse')])
				}
				if (frappe.query_report.get_filter_value('vehicle')) {
					filters.push(['Stock Entry', 'vehicle', '=', frappe.query_report.get_filter_value('vehicle')])
				}
				if (frappe.query_report.get_filter_value('driver')) {
					filters.push(['Stock Entry', 'driver', '=', frappe.query_report.get_filter_value('driver')])
				}
				if (frappe.query_report.get_filter_value('operator')) {
					filters.push(['Stock Entry', 'operator', '=', frappe.query_report.get_filter_value('operator')])
				}

				return frappe.db.get_list("Stock Entry", {
					filters: filters,
					group_by: "t_warehouse",
					fields: ['`tabStock Entry Detail`.t_warehouse as value', '`tabStock Entry Detail`.t_warehouse as description'],
					limit: 0
				});
			}
		},
		{
			fieldname: 'vehicle',
			label: __('Vehicle'),
			fieldtype: 'Link',
			options: 'Vehicle',
			get_query: () => {
				return {
					filters: {
						name: ["in", vehicles]
					}
				}
			}
		},
		{
			fieldname: 'driver',
			label: __('Driver'),
			fieldtype: 'Link',
			options: 'Driver',
			get_query: () => {
				return {
					filters: {
						name: ["in", drivers]
					}
				}
			}
		},
		{
			fieldname: 'operator',
			label: __('Operator'),
			fieldtype: 'Link',
			options: 'Driver',
			get_query: () => {
				return {
					filters: {
						name: ["in", operators]
					}
				}
			}
		},
		{
			fieldname: 'group_by',
			label: __('Group By'),
			fieldtype: 'MultiSelectList',
			get_data: function (txt) {
				return [
					{
						value: 'Date',
						description: ''
					},
					{
						value: 'Item',
						description: ''
					},
				]
			},
			on_change: () => {
				if (frappe.query_report.get_filter_value('report_type') == 'Summary' && !frappe.query_report.get_filter_value('group_by')?.length) {
					frappe.show_alert({
						message: '<b>Summary</b> will be generated based on the <b>Group By<b>',
						indicator: 'yellow'
					});
				}
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: 'also_group_by',
			label: __('Also Group By'),
			fieldtype: 'MultiSelectList',
			get_data: function (txt) {
				return [
					{
						value: 'Vehicle',
						description: ''
					},
					{
						value: 'Driver',
						description: ''
					},
					{
						value: 'Operator',
						description: ''
					}
				];
			},
			depends_on: "eval: frappe.query_report.get_filter_value('group_by')?.length"
		},
		{
			fieldname: 'report_type',
			label: __('Report Type'),
			fieldtype: 'Select',
			options: 'Report\nSummary',
			default: 'Report',
			on_change: () => {
				if (frappe.query_report.get_filter_value('report_type') == 'Summary' && !frappe.query_report.get_filter_value('group_by')?.length) {
					frappe.show_alert({
						message: '<b>Summary</b> will be generated based on the <b>Group By<b>',
						indicator: 'yellow'
					});
				}
				frappe.query_report.refresh();
			}
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = __(default_formatter(value, row, column, data));
		if (data && ["Group Total", "Total"].includes(data.item_code)) {
			value = `<b>${value}</b>`
		}

		if (column.fieldname == 'posting_date' && ['Group Total', 'Total'].includes(data.item_code)) {
			value = `<b>${data.item_code}</b>`
		}

		return value
	}
};

let setup_filters_fn = frappe.query_report.setup_filters;

frappe.query_report.setup_filters = (...args) => {
	setup_filters_fn.call(frappe.query_report, ...args)
	frappe.query_report.set_filter_value('group_by', ['Date']);
}
