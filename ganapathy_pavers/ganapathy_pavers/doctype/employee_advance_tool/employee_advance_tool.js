	
frappe.ui.form.on("Employee Advance Tool",{
	designation:function(frm,cdt,cdn){
		var advance=locals[cdt][cdn]
		var advance1=advance.designation
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.employee_advance_tool.employee_advance_tool.employee_finder",
			args:{
				advance1: advance1,
				location:frm.doc.location
			},
			callback(r){
				frm.clear_table("employee_advance_details");
				for(var i=0;i<r.message.length;i++){
					var child = cur_frm.add_child("employee_advance_details");
					frappe.model.set_value(child.doctype, child.name, "employee", r.message[i]["name"])
					frappe.model.set_value(child.doctype, child.name, "employee_name", r.message[i]["employee_name"])
					frappe.model.set_value(child.doctype, child.name, "designation", advance1)
					if (frm.doc.designation == "Labour Worker"){
						frappe.model.set_value(child.doctype, child.name, "payment_method",'Deduct from Salary')
					}
				}
				cur_frm.refresh_field("employee_advance_details")
			}
		})

	},
	location: function(frm) {
		frm.trigger("designation")
	}	
})