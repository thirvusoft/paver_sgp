// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Maintenance', {
	refresh: async function (frm) {
		if (frm.is_new()) {
			frm.set_value("time", frappe.datetime.now_time())
			let fi = await frappe.db.get_doc("DSM Defaults"),
				raw = await frappe.db.get_doc("DSM Defaults")
			fi.warehouse_for_pavers_and_compound_walls.forEach(row => {
				let newrow = frm.add_child("warehouse")
				newrow.warehouse = row.warehouse
			})
			refresh_field('warehouse')
			raw.warehouse_for_colour_powder_items.forEach(row => {
				let newrow = frm.add_child("warehouse_colour")
				newrow.warehouse = row.warehouse
			})
			refresh_field('warehouse_colour')
		}
	},
	get_attendance_details: function (frm) {
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.get_attendance_details",
			args: {
				date: cur_frm.doc.date || cur_frm.scroll_to_field('date') + frappe.throw({ message: "Please enter <b>Date</b> to fetch Attendance details", title: "Missing Fields", indicator: "red" }),
			},
			callback: function (res) {
				cur_frm.set_value('labour_present', res['message']['labour_present']);
				cur_frm.set_value('operator_present', res['message']['operator_present']);
				cur_frm.set_value('labour_absent', res['message']['labour_absent']);
				cur_frm.set_value('operator_absent', res['message']['operator_absent']);
			}
		});
	},
	load_item_details: function (frm) {
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.daily_maintenance.daily_maintenance.paver_item",
			args: {
				warehouse: cur_frm.doc.warehouse.length ? cur_frm.doc.warehouse : cur_frm.scroll_to_field('warehouse') + frappe.throw({ message: "Please enter <b>Warehouse for Pavers and Compound Walls</b>", title: "Missing Fields", indicator: "red" }),
				production_date: cur_frm.doc.production_date || cur_frm.scroll_to_field('production_date') + frappe.throw({ message: "Please enter <b>Production Date</b> to fetch production details", title: "Missing Fields", indicator: "red" }),
				date: cur_frm.doc.date || cur_frm.scroll_to_field('date') + frappe.throw({ message: "Please enter <b>Date</b> to fetch production and vehicle details", title: "Missing Fields", indicator: "red" }),
				time: cur_frm.doc.time || cur_frm.scroll_to_field('time') + frappe.throw({ message: "Please enter <b>Time</b> to fetch production and vehicle details", title: "Missing Fields", indicator: "red" }),
				warehouse_colour: cur_frm.doc.warehouse_colour.length ? cur_frm.doc.warehouse_colour : cur_frm.scroll_to_field('warehouse_colour') + frappe.throw({ message: "Please enter <b>Warehouse for Colour Powder Items</b>", title: "Missing Fields", indicator: "red" })
			},
			freeze: true,
			freeze_message: ganapathy_pavers.loading_svg || "Fetching data...",
			callback: function (r) {
				cur_frm.set_value('colour_details', r.message[0])
				cur_frm.set_value('normal_colour_total', r.message[1])
				cur_frm.set_value('colour_details_of_sb', r.message[2])
				cur_frm.set_value('shot_blast_colour_total', r.message[3])
				cur_frm.set_value("vehicle_details", r.message[4])
				cur_frm.set_value("machine_details", r.message[5])
				cur_frm.set_value("compound_wall_stock", r.message[6])
				cur_frm.set_value("colour_powder", r.message[7])
				cur_frm.set_value("compound_wall_item_stock", r.message[8])
				cur_frm.set_value("size_details", r.message[9])
				cur_frm.set_value("raw_material_details", r.message[10])
				cur_frm.set_value("other_cw_items", r.message[11])
			}
		})
	},
	load_current_stock: function (frm) {
		cur_frm.trigger("load_item_details")
	},
});
