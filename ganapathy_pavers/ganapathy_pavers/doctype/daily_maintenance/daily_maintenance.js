// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Maintenance', {
	 load_item_details: function(frm) {
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.paver_item",
			args:{warehouse:cur_frm.doc.warehouse},
			callback:function(r){
				cur_frm.set_value('colour_details', r.message[0])
				cur_frm.set_value('red_total_n', r.message[1]['red'])
				cur_frm.set_value('black_total_n',r.message[1]['black'])
				cur_frm.set_value('grey_total_n', r.message[1]['grey'])
				cur_frm.set_value('brown_total_n', r.message[1]['brown'])
				cur_frm.set_value('yellow_total_n',r.message[1]['yellow'])
			}

		})
	}
	
});
