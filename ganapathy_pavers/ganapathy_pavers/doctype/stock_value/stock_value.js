// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Value', {
	refresh: async function (frm) {
		if (frm.is_new()) {
			let DSM_DEF = await frappe.db.get_doc("DSM Defaults");

			DSM_DEF.warehouse_for_pavers_and_compound_walls.forEach(row => {
				let newrow = frm.add_child("warehouse_paver_cw")
				newrow.warehouse = row.warehouse
			})
			refresh_field('warehouse_paver_cw')
			DSM_DEF.warehouse_for_colour_powder_items.forEach(row => {
				let newrow = frm.add_child("warehouse_rm")
				newrow.warehouse = row.warehouse
			})
			refresh_field('warehouse_rm')
		}
	},
	get_items: async function (frm) {
		let rm_warehouse = [], paver_cw_warehouse = [];
		(frm.doc.warehouse_rm || []).forEach(row => {
			if (row.warehouse && !rm_warehouse.includes(row.warehouse)) {
				rm_warehouse.push(row.warehouse);
			}
		});
		(frm.doc.warehouse_paver_cw || []).forEach(row => {
			if (row.warehouse && !paver_cw_warehouse.includes(row.warehouse)) {
				paver_cw_warehouse.push(row.warehouse);
			}
		});

		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.stock_value.stock_value.get_items",
			freeze: true,
			freeze: 'Fetching Items',
			args: {
				item_group: frm.doc.item_group,
				cw_type: frm.doc.cw_type,
				date: frm.doc.date,
				paver_cw_warehouse: paver_cw_warehouse,
				rm_warehouse: rm_warehouse,
				ignore_empty_item_size: frm.doc.ignore_empty_item_size
			},
			callback: (r) => {
				Object.keys(r.message).forEach(key => {
					frm.set_value(key, r.message[key]);
					refresh_field(key);
				});
			}
		});
	}
});
