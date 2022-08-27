// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Tool Settings', {
	clear_dialogs: function(frm){
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.attendance_tool_settings.attendance_tool_settings.clear_dialogs",
			callback: function(){
				frappe.show_alert({message: 'All Prompts are Cleared.'})
			}
		})
	},
	after_save: function(frm){
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.attendance_tool_settings.attendance_tool_settings.after_save",
		})
	}
});
