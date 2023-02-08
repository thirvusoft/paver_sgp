// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var acc_filters = []
frappe.ui.form.on('Maintenance type', {
	refresh: async function (frm) {
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_child_under_vehicle_expense",
			callback(r) {
				acc_filters = r.message;
			}
		});
		frm.set_query("expense_account", function () {
			return {
				filters: {
					name: ['in', acc_filters],
					is_group: 0
				}
			}
		});

		make_fields(frm.doc.__onload.vl_fields);
	},
});

function make_fields(fields) {
	let vl_field_options = []
	fields.forEach(field => {
		vl_field_options.push({
			label: `${__(field.label)} (${field.parent})`,
			value: `${field.parent}.${field.fieldname}`
		});
	})
	var attr_html = cur_frm.fields_dict.choose_fields.wrapper;
	attr_html.innerHTML = ''
	let form_fields = [{
		fieldname: "vl_field",
		label: "Choose Field",
		fieldtype: "Autocomplete",
		options: vl_field_options,
		default: `${cur_frm.doc.vl_doctype || ""}.${cur_frm.doc.vl_fieldname || ""}`,
		description: "Choose any field from the list of Vehicle Log fields"
	}]
	var form = new frappe.ui.FieldGroup({
		fields: form_fields, body: attr_html
	});
	form.make();
	form.fields.forEach(field => {
		field.onchange = function () {
			let _field = form.get_value(field.fieldname)?.split('.')
			cur_frm.set_value("vl_fieldname", _field[1] || "");
			cur_frm.set_value("vl_doctype", _field[0] || "")
			if (_field[0]) {
				cur_frm.set_value("vl_tab_doctype", `tab.${_field[0]}`)
			} else {
				cur_frm.set_value("vl_tab_doctype", "")
			}
		}
	})


}