// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Value', {
	refresh: function (frm) {
		document.querySelector(`button[data-fieldtype="Button"][data-fieldname="get_items"]`).classList.add('btn-primary')
		let btn = frm.add_custom_button("Get Items", () => {
			frm.trigger('get_items');
		}).addClass('btn-primary');

		function btnVisible() {
			window.requestAnimationFrame(btnVisible);
			if (ganapathy_pavers.isVisible(document.querySelector(`button[data-fieldtype="Button"][data-fieldname="get_items"]`))) {
				btn[0].style.display = "none"
			} else {
				btn[0].style.display = ""
			}
		}

		try {
			btnVisible();;
		} catch (error) {
			console.log('Error caught:', error);
		}

		if (frm.is_new()) {
			frm.set_value("time", frappe.datetime.now_time());
		}
	},
	unit: async function (frm) {
		if (frm.doc.unit) {
			let ac = await frappe.db.get_value("Stock Defaults", frm.doc.unit, "administrative_cost");
			frm.set_value("administrative_cost", ac.message.administrative_cost || 0);			
		}
	},
	get_warehouses: async function (frm) {
		if (!frm.doc.unit) {
			frm.scroll_to_field('unit');
			frappe.show_alert({ message: 'Please enter Unit', indicator: 'red' });
			return
		}
		frm.set_value("warehouse_paver_cw", []);
		frm.set_value("warehouse_rm", []);

		let STOCK_DEF_LIST = await frappe.db.get_list('Stock Defaults', { filters: { 'unit': frm.doc.unit } });

		if (!STOCK_DEF_LIST.length) {
			frappe.throw({ message: `Please create <a href='/app/stock-defaults/'><b>Stock Defaults</b></a> for ${frm.doc.unit}`, indicator: 'red' })
		}

		let STOCK_DEF = await frappe.db.get_doc("Stock Defaults", frm.doc.unit);

		STOCK_DEF.warehouse_for_pavers_and_compound_walls.forEach(row => {
			let newrow = frm.add_child("warehouse_paver_cw")
			newrow.warehouse = row.warehouse
		});
		refresh_field('warehouse_paver_cw');

		let rm_warehouses = [];
		STOCK_DEF.warehouse_for_colour_powder_items.forEach(row => {
			if (!rm_warehouses.includes(row.warehouse)) {
				let newrow = frm.add_child("warehouse_rm")
				newrow.warehouse = row.warehouse

				rm_warehouses.push(row.warehouse);
			}
		});

		STOCK_DEF.raw_material_details.forEach(row => {
			if (!rm_warehouses.includes(row.warehouse)) {
				let newrow = frm.add_child("warehouse_rm")
				newrow.warehouse = row.warehouse

				rm_warehouses.push(row.warehouse);
			}
		});
		refresh_field('warehouse_rm');
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
		if (!frm.doc.unit) {
			frappe.throw({ message: 'Please enter Unit' })
		}
		await frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.stock_value.stock_value.get_items",
			freeze: true,
			freeze_message: ganapathy_pavers.loading_svg || 'Fetching Items',
			args: {
				unit: frm.doc.unit,
				administrative_cost: frm.doc.administrative_cost || 0,
				_type: frm.doc.type,
				date: frm.doc.date,
				time: frm.doc.time,
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
