// Copyright (c) 2022, thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interakt Settings', {
		refresh: function(frm,cdt,cdn) {
		   {
				frm.add_custom_button(__('Link to Interakt'),function(){
					var data=locals[cdt][cdn]
					let args= {
						api_endpoint : data.api_endpoint,
						api_key : data.api_key,
						contact : data.contact_no,
						template : data.template_box,
						url : data.url,

					}
					frappe.call({
						method: "interakt.api.interaktsettings",
						args:args
					});
				   
				} )
		}
	}
	})
	
