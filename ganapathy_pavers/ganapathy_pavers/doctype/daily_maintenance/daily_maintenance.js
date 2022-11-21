// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Maintenance', {
	 load_item_details: function(frm) {
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.paver_item",
			args:{warehouse:cur_frm.doc.warehouse,date:cur_frm.doc.date, warehouse_colour:cur_frm.doc.warehouse_colour},
			callback:function(r){
				cur_frm.set_value('colour_details', r.message[0])
				cur_frm.set_value('red_total_n', r.message[1]['red'])
				cur_frm.set_value('black_total_n',r.message[1]['black'])
				cur_frm.set_value('grey_total_n', r.message[1]['grey'])
				cur_frm.set_value('brown_total_n', r.message[1]['brown'])
				cur_frm.set_value('yellow_total_n',r.message[1]['yellow'])
				cur_frm.set_value('colour_details_of_sb', r.message[2])
				cur_frm.set_value('red_total_s', r.message[3]['red'])
				cur_frm.set_value('black_total_s',r.message[3]['black'])
				cur_frm.set_value('grey_total_s', r.message[3]['grey'])
				cur_frm.set_value('brown_total_s', r.message[3]['brown'])
				cur_frm.set_value('yellow_total_s',r.message[3]['yellow'])
				cur_frm.set_value("vehicle_details", r.message[4])
				cur_frm.set_value("machine_details", r.message[5])
				cur_frm.set_value("compound_wall_stock", r.message[6])
				cur_frm.set_value("colour_powder", r.message[7])

				
			}

		})
	}
	
});
