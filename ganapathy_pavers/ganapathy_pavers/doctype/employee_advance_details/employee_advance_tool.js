frappe.ui.form.on('Employee Advance Tool',{
    refresh: function (frm) {
		if (frm.doc.docstatus == 0) {
			if (!frm.is_new()) {
				frm.page.clear_primary_action();
				frm.add_custom_button(__("Get Employees"),
					function () {
						frm.events.get_employee_details(frm);
					}
				).toggleClass('btn-primary', !(frm.doc.employees || []).length);
			}
			if ((frm.doc.employees || []).length && !frappe.model.has_workflow(frm.doctype)) {
				frm.page.clear_primary_action();
				frm.page.set_primary_action(__('Create Employee'), () => {
					frm.save('Submit').then(() => {
						frm.page.clear_primary_action();
						frm.refresh();
						frm.events.refresh(frm);
					});
				});
			}
		}
		if (frm.doc.docstatus == 1) {
			if (frm.custom_buttons) frm.clear_custom_buttons();
			frm.events.add_context_buttons(frm);
		}
	},

	// get_employee_details: function (frm) {
	// 	console.log('test');
	// 	return frappe.call({
	// 		method: "employee_advance_details",
	// 		doc: frm.doc
	// 	}).then(r => {
	// 		if (r.docs && r.docs[0].employees) {
	// 			frm.employees = r.docs[0].employees;
	// 			frm.dirty();
	// 			frm.save();
	// 			frm.refresh();
	// 			if (r.docs[0].validate_attendance) {
	// 				render_employee_attendance(frm, r.message);
	// 			}
	// 		}
	// 	})
	// },
	get_employee_details: function(frm) {
		// if(frm.doc.closed_documents.length === 0 || (frm.doc.closed_documents.length === 1 && frm.doc.closed_documents[0].document_type == undefined)) {
			frappe.call({
				method: "employee_advance_details",
				doc:frm.doc,
				callback: function(r) {
					// if(r.message) {
					// 	cur_frm.clear_table("closed_documents");
					// 	r.message.forEach(function(element) {
					// 		var c = frm.add_child("closed_documents");
					// 		c.document_type = element.document_type;
					// 		c.closed = element.closed;
					// 	});
					// 	refresh_field("closed_documents");
					// }
				}
			});
		// }
	}
			})
			