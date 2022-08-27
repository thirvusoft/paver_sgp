// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
	
frappe.ui.form.on("Employee Bonus Tool",{
	designation:function(frm,cdt,cdn){
		var advance=locals[cdt][cdn]
		var advance1=advance.designation
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.employee_bonus_tool.employee_bonus_tool.employee_finder",
			args:{advance1},
			callback(r){
				frm.clear_table("employee_bonus_details");
				for(var i=0;i<r.message.length;i++){
					var child = cur_frm.add_child("employee_bonus_details");
					frappe.model.set_value(child.doctype, child.name, "employee", r.message[i]["name"])
					frappe.model.set_value(child.doctype, child.name, "employee_name", r.message[i]["employee_name"])
					frappe.model.set_value(child.doctype, child.name, "designation", advance1)
					if (frm.doc.designation == "Labour Worker"){
						frappe.model.set_value(child.doctype, child.name, "payment_method",'Deduct from Salary')
					}
				}
				cur_frm.refresh_field("employee_bonus_details")
			}
		})

	},
	on_submit:function(frm,cdt,cdn){
		var advance=locals[cdt][cdn]
		for(var i=0;i<advance.employee_bonus_details.length;i++){
			frappe.call({
				method:"ganapathy_pavers.ganapathy_pavers.doctype.employee_bonus_tool.employee_bonus_tool.create_retention_bonus",
				args:{amount:advance.employee_bonus_details[i].current_bonus,
					name:advance.employee_bonus_details[i].employee,
					date:frm.doc.date},
			})
		}
	},
	before_save:function(frm, cdt, cdn) {
		var table = frm.doc.employee_bonus_details;
		var total = 0;
		for(var i in table) {
			total = total + table[i].current_bonus;
		 }
		 frm.set_value("total_bonus_amount",total);
		}
});
	