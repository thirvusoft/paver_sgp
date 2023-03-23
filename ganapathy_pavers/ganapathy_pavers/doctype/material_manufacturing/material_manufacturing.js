// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var uom_nos = 0
var uom_bundle = 0
frappe.ui.form.on('Material Manufacturing', {
	refresh: async function (frm) {
		if (cur_frm.is_new() == 1) {
			if (frm.doc.is_shot_blasting) {
				default_value("shot_blast_per_sqft", "shot_blast_per_sqft")
			}
			// default_value("labour_cost_per_sqft", "labour_cost_per_sqft")
			default_value("strapping_cost_per_sqft", "strapping_cost_per_sqft")
			default_value("default_manufacture_operation", "operation")
			default_value("default_rack_shift_workstation", "workstation")
			default_value("default_manufacture_workstation", "work_station")
			default_value("default_manufacture_source_warehouse", "source_warehouse")
			default_value("default_manufacture_target_warehouse", "target_warehouse")
			default_value("default_rack_shift_source_warehouse", "rack_shift_source_warehouse")
			default_value("default_rack_shift_target_warehouse", "rack_shift_target_warehouse")
			default_value("default_curing_source_warehouse", "curing_source_warehouse")
			default_value("default_curing_target_warehouse", "curing_target_warehouse")
			default_value("setting_oil", "setting_oil_item_name")
			frm.trigger("get_bin_items")
		}
		set_css(frm);
	},
	get_bin_items: async function (frm) {
		frm.clear_table("bin_items");
		frm.fields_dict.bin_items?.refresh()
		await frappe.db.get_doc("USB Setting").then(bin_items_map => {
			(bin_items_map.item_bin_select || []).forEach(bin => {
				let row = frm.add_child("bin_items")
				row.item_code = bin.item_code
				row.bin = bin.bin
			});
			frm.fields_dict.bin_items?.refresh()
		})
	},
	validate: function (frm) {
		if (frm.doc.is_shot_blasting && !frm.doc.shot_blast_per_sqft) {
			frappe.throw({ title: "Mandatory Fields", message: "Please enter value for <b>Shot Blast per Sqft</b>" })
		}
		(frm.doc.items || []).forEach(row => {
			if (row.layer_type == 'Panmix') {
				row.no_of_batches = frm.doc.bottom_layer_batches
			}
		});
	},
	item_to_manufacture: function (frm) {
		if (frm.doc.item_to_manufacture) {
			if (frm.doc.item_to_manufacture.includes("SHOT BLAST")) {
				cur_frm.set_value("is_shot_blasting", 1)
			}
			else {
				cur_frm.set_value("is_shot_blasting", 0)
			}
		}
		frappe.db.get_list("BOM", { filters: { "item": frm.doc.item_to_manufacture, "is_default": 1, "docstatus": 1, "is_active": 1 }, fields: ["name"] }).then((r) => {
			if (r.length != 0) {
				cur_frm.set_value("bom_no", r[0].name)
			}
		})
	},
	is_shot_blasting: function (frm) {
		if (frm.doc.is_shot_blasting == 1) {
			default_value("shot_blast_per_sqft", "shot_blast_per_sqft")
			default_value("default_curing_target_warehouse_for_setting", "curing_target_warehouse")
		}
		else {
			frm.set_value("shot_blast_per_sqft", 0)
			default_value("default_curing_target_warehouse", "curing_target_warehouse")
		}
	},
	from_time: function (frm) {
		var field = "ts_total_hours"
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to, cur_frm.doc.hours_to_reduce_manufacture)
	},
	to: function (frm) {
		var field = "ts_total_hours"
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to, cur_frm.doc.hours_to_reduce_manufacture)
	},
	hours_to_reduce_manufacture: function (frm) {
		var field = "ts_total_hours"
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to, cur_frm.doc.hours_to_reduce_manufacture)
	},
	from_time_rack: function (frm) {
		var field = "total_hours_rack"
		total_hrs(frm, field, frm.doc.from_time_rack, frm.doc.to_time_rack, cur_frm.doc.hours_to_reduce_rack)
	},
	to_time_rack: function (frm) {
		var field = "total_hours_rack"
		total_hrs(frm, field, frm.doc.from_time_rack, frm.doc.to_time_rack, cur_frm.doc.hours_to_reduce_rack)
	},
	hours_to_reduce_rack: function (frm) {
		var field = "total_hours_rack"
		total_hrs(frm, field, frm.doc.from_time_rack, frm.doc.to_time_rack, cur_frm.doc.hours_to_reduce_rack)
	},
	from_time_curing: function (frm) {
		var field = "total_hrs"
		total_hrs(frm, field, frm.doc.from_time_curing, frm.doc.to_time_curing, 0)
	},
	to_time_curing: function (frm) {
		var field = "total_hrs"
		total_hrs(frm, field, frm.doc.from_time_curing, frm.doc.to_time_curing, 0)
	},
	no_of_bundle: function (frm) {
		cur_frm.set_value("shot_blasted_bundle", frm.doc.no_of_bundle)
	},
	shot_blasted_bundle: function (frm) {
		if (frm.doc.shot_blasted_bundle == 0 && frm.doc.is_shot_blasting) {
			cur_frm.set_value("status1", "Completed")
		}
	},
	additional_cost: function (frm) {
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense + frm.doc.total_raw_material);
	},
	total_raw_material: function (frm) {
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense + frm.doc.total_raw_material);
	},
	rack_shifting_additional_cost: function (frm) {
		cur_frm.set_value('rack_shifting_total_expense1', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost)
	},
	strapping_cost: function (frm) {
		cur_frm.set_value('rack_shifting_total_expense1', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost)
	},
	production_qty: function (frm) {
		cur_frm.set_value('total_completed_qty', frm.doc.production_qty - frm.doc.damage_qty)
		frappe.db.get_value("Item", { "name": frm.doc.item_to_manufacture }, "pavers_per_sqft", (sqft) => {
			cur_frm.set_value('production_sqft', frm.doc.total_completed_qty / sqft.pavers_per_sqft)
		});
	},
	damage_qty: function (frm) {
		cur_frm.set_value('total_completed_qty', frm.doc.production_qty - frm.doc.damage_qty)
		frappe.db.get_value("Item", { "name": frm.doc.item_to_manufacture }, "pavers_per_sqft", (sqft) => {
			cur_frm.set_value('production_sqft', frm.doc.total_completed_qty / sqft.pavers_per_sqft)
		});
	},
	curing_damaged_qty: function (frm) {
		cur_frm.set_value('no_of_bundle', frm.doc.no_of_bundle - frm.doc.curing_damaged_qty)
	},
	rack_shift_damage_qty: function (frm) {
		cur_frm.set_value('total_no_of_produced_qty', frm.doc.total_no_of_produced_qty - frm.doc.rack_shift_damage_qty)
	},
	rate_per_hrs: function (frm) {
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs) / frm.doc.no_of_division)
	},
	total_hrs: function (frm) {
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs) / frm.doc.no_of_division)
	},
	no_of_division: function (frm) {
		cur_frm.set_value('labour_cost', (frm.doc.rate_per_hrs * frm.doc.total_hrs) / frm.doc.no_of_division)
	},
	before_save: function (frm) {
		if (frm.is_new()) {
			frm.trigger("total_cost");
		} else if (!frm.doc.labour_cost_manufacture || !frm.doc.operators_cost_in_manufacture) {
			frm.scroll_to_field("total_cost");
			frm.scroll_to_field("labour_cost_manufacture");
			frm.scroll_to_field("operators_cost_in_manufacture");
			frappe.show_alert({ message: "Please fill Labour and Operator Cost", indicator: "red" });
		}

		std_item(frm)
		if (frm.doc.docstatus == 0) {
			if (frm.doc.ts_total_hours > 0 && frm.doc.docstatus == 0) {
				cur_frm.set_value('total_manufacturing_expense', frm.doc.labour_cost_manufacture + frm.doc.operators_cost_in_manufacture);
				cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense + frm.doc.total_raw_material);
			}
			if (frm.doc.total_hours_rack > 0 && frm.doc.docstatus == 0) {
				cur_frm.set_value('total_rack_shift_expense', frm.doc.labour_cost_in_rack_shift + frm.doc.operators_cost_in_rack_shift);
				cur_frm.set_value('rack_shifting_total_expense1', frm.doc.rack_shifting_additional_cost + frm.doc.total_rack_shift_expense + frm.doc.strapping_cost);
			}
			// frappe.call({
			// 	method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.find_batch",
			// 	args: {
			// 		name: frm.doc.name,
			// 	},
			// 	callback(r) {
			// 		if (r.message) {
			// 			cur_frm.set_value('batch_no_manufacture', r.message[0]);
			// 			cur_frm.set_value('batch_no_rack_shifting', r.message[1]);
			// 			cur_frm.set_value('batch_no_curing', r.message[2]);
			// 		}
			// 	}
			// })

		}
	},
	strapping_cost_per_sqft: function (frm) {
		cur_frm.set_value('strapping_cost', frm.doc.strapping_cost_per_sqft * frm.doc.production_sqft);
	},
	total_completed_qty: function (frm) {
		cur_frm.set_value('total_no_of_produced_qty', frm.doc.total_completed_qty);
	},
	total_no_of_produced_qty: function (frm) {
		frm.set_value("remaining_qty", 0)
		var bundle_cf = 0
		var nos_cf = 0
		var default_cf = 0
		frappe.db.get_single_value("USB Setting", "default_manufacture_uom").then(value => {
			uom_nos = value
		})
		frappe.db.get_single_value("USB Setting", "default_rack_shift_uom").then(value => {
			uom_bundle = value
		})
		frappe.db.get_doc('Item', frm.doc.item_to_manufacture).then((doc) => {
			var default_uom = doc.stock_uom
			for (var i of doc.uoms) {
				if (uom_bundle == i.uom) {
					bundle_cf = i.conversion_factor
				}
				if (uom_nos == i.uom) {
					nos_cf = i.conversion_factor
				}
				if (default_uom == i.uom) {
					default_cf = i.conversion_factor
				}
			}
			var total_amount = (frm.doc.total_no_of_produced_qty * nos_cf) / bundle_cf
			if (total_amount >= 1) {
				cur_frm.set_value('total_no_of_bundle', total_amount);
			}
			else {
				cur_frm.set_value('total_no_of_bundle', 0);
			}
		});
	},
	total_no_of_bundle: function (frm) {
		cur_frm.set_value('no_of_bundle', frm.doc.total_no_of_bundle);
	},
	onload: function (frm) {
		frm.set_query("source_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		// var company = frappe.get_single('Global Defaults').default_company
		// cur_frm.set_value("company",company)

		frm.set_query("target_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		frm.set_query("rack_shift_source_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		frm.set_query("rack_shift_target_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		frm.set_query("curing_source_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		frm.set_query("curing_target_warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", "0"]
				]
			}
		})
		frm.set_query("item_code", "bin_items", function () {
			return {
				"filters": {
					item_group: "Raw Material"
				}
			}
		})
		frm.set_query("item_to_manufacture", function () {
			return {
				filters: [
					['Item', 'item_group', '=', 'Pavers']
				]
			}
		})
		frm.set_query("bom_no", function () {
			return {
				"filters": {
					item: frm.doc.item_to_manufacture,
					is_active: 1
				}
			}
		})
		frm.set_query("machine_operator", function () {
			return {
				"filters": {
					designation: 'Operator',
				}
			}
		})
		frm.set_query("panmix_operator", function () {
			return {
				"filters": {
					designation: 'Operator'
				}
			}
		})
	},
	create_stock_entry: function (frm) {
		make_stock_entry(frm, "create_stock_entry")
	},
	create_rack_shiftingstock_entry: function (frm) {
		make_stock_entry(frm, "create_rack_shiftingstock_entry")
	},
	curing_stock_entry: function (frm) {
		make_stock_entry(frm, "curing_stock_entry")
	},
	total_cost: function (frm) {
		cur_frm.set_value('operators_cost_in_manufacture', (frm.doc.operator_cost_workstation / ((frm.doc.no_of_item_in_process > 1) ? (frm.doc.total_working_hrs ? frm.doc.total_working_hrs : 1) : frm.doc.ts_total_hours) * frm.doc.ts_total_hours))
		cur_frm.set_value('labour_cost_manufacture', frm.doc.labour_cost_in_manufacture * frm.doc.ts_total_hours * frm.doc.no_of_labours)
	},
	total_no_of_batches: function (frm) {
		for (let row = 0; row < (frm.doc.items ? frm.doc.items.length : 0); row++) {
			let cdt = frm.doc.items[row].doctype, cdn = frm.doc.items[row].name;
			let data = locals[cdt][cdn]
			if (data.layer_type == "Top Layer") {
				frappe.model.set_value(cdt, cdn, 'qty', (data.ts_qty ? data.ts_qty : 0) * (frm.doc.total_no_of_batches ? frm.doc.total_no_of_batches : 0))
				frappe.model.set_value(cdt, cdn, 'no_of_batches', (frm.doc.total_no_of_batches ? frm.doc.total_no_of_batches : 0))
			}
		}
		refresh_field("items")
	},
	bottom_layer_batches: function (frm) {
		for (let row = 0; row < (frm.doc.items ? frm.doc.items.length : 0); row++) {
			let cdt = frm.doc.items[row].doctype, cdn = frm.doc.items[row].name;
			let data = locals[cdt][cdn]
			if (data.layer_type == "Panmix") {
				frappe.model.set_value(cdt, cdn, 'no_of_batches', (frm.doc.bottom_layer_batches ? frm.doc.bottom_layer_batches : 0))
			}
		}
		refresh_field("items")
	},
	no_of_labours: function (frm) {
		cur_frm.set_value('labour_cost_manufacture', frm.doc.labour_cost_in_manufacture * frm.doc.ts_total_hours * frm.doc.no_of_labours)
	},
	no_of_labours2: function (frm) {
		cur_frm.set_value('labour_cost_in_rack_shift', frm.doc.labour_ws_cost * frm.doc.total_hours_rack * frm.doc.no_of_labours2)
	},
	total_hours_rack: function (frm) {
		cur_frm.set_value('labour_cost_in_rack_shift', frm.doc.labour_ws_cost * frm.doc.total_hours_rack * frm.doc.no_of_labours2)
	},
	workstation: async function (frm) {
		if (frm.doc.workstation) {
			await frappe.db.get_value('Workstation', frm.doc.workstation, 'no_of_labours').then((value) => {
				cur_frm.set_value('no_of_labours2', value.message.no_of_labours)
			})
		}
		else {
			cur_frm.set_value('no_of_labours2', 0)
		}
	},
	work_station: async function (frm) {
		if (frm.doc.work_station) {
			await frappe.db.get_value('Workstation', frm.doc.work_station, 'no_of_labours').then((value) => {
				cur_frm.set_value('no_of_labours', value.message.no_of_labours)
			})
		}
		else {
			cur_frm.set_value('no_of_labours', 0)
		}
	},
	operator_cost_rack_shift: function (frm) {
		cur_frm.set_value('operators_cost_in_rack_shift', (frm.doc.operator_cost_rack_shift / ((frm.doc.no_of_item_in_process > 1) ? (frm.doc.total_working_hrs ? frm.doc.total_working_hrs : 1) : 1) * frm.doc.total_hours_rack))
	},
	operators_cost_in_rack_shift: function (frm) {
		cur_frm.set_value('total_rack_shift_expense', frm.doc.labour_cost_in_rack_shift + frm.doc.operators_cost_in_rack_shift);
	},
	labour_cost_in_rack_shift: function (frm) {
		cur_frm.set_value('total_rack_shift_expense', frm.doc.labour_cost_in_rack_shift + frm.doc.operators_cost_in_rack_shift);
	},
	no_of_racks: function (frm) {
		production_qty_calc(frm)
	},
	no_of_plates1: function (frm) {
		production_qty_calc(frm)
	}
});

function production_qty_calc(frm) {
	cur_frm.set_value('production_qty', (cur_frm.doc.no_of_racks ? cur_frm.doc.no_of_racks : 0) * (cur_frm.doc.per_rack ? cur_frm.doc.per_rack : 0) + (cur_frm.doc.no_of_plates1 ? cur_frm.doc.no_of_plates1 : 0) * (cur_frm.doc.per_plate ? cur_frm.doc.per_plate : 0))
}

function make_stock_entry(frm, type1) {
	frappe.call({
		method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.make_stock_entry",
		args: {
			doc: frm.doc,
			type1: type1
		},
		callback: async function (r) {
			await cur_frm.reload_doc()
			cur_frm.save()
		}
	})
}
function total_hrs(frm, field, from, to, red) {
	frappe.call({
		method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_hrs",
		args: {
			from_time: from,
			to: to
		},
		callback(r) {
			cur_frm.set_value(field, r.message ? r.message - red : 0 - red);
		}
	})
}

function add_total_raw_material(frm) {
	let total_bundle = 0, top_layer = 0, bottom_layer = 0;
	if (frm.doc.items)
		for (var i = 0; i < (frm.doc.items ? frm.doc.items.length : 0); i++) {
			total_bundle += frm.doc.items[i].amount ? frm.doc.items[i].amount : 0
			if (frm.doc.items[i].layer_type == "Top Layer") {
				top_layer += frm.doc.items[i].amount ? frm.doc.items[i].amount : 0
			}
			if (frm.doc.items[i].layer_type == "Panmix") {
				bottom_layer += frm.doc.items[i].amount ? frm.doc.items[i].amount : 0
			}
			// if(frm.doc.items[i].amount == 0){
			// 	frappe.throw("Kindly Enter Rate in Item Table")
			// }
		}
	cur_frm.set_value('total_raw_material', total_bundle);
	cur_frm.set_value('top_layer_cost', top_layer);
	cur_frm.set_value('bottom_layer_cost', bottom_layer);
	if (frm.doc.setting_oil_item_name) {
		cur_frm.set_value('total_setting_oil_qty', ((frm.doc.bottom_layer_batches || 0) * frm.doc.setting_oil_qty) / 1000)
	}
	if (frm.doc.ts_total_hours > 0 && frm.doc.docstatus == 0) {
		cur_frm.set_value('total_manufacturing_expense', frm.doc.labour_cost_manufacture + frm.doc.operators_cost_in_manufacture);
		cur_frm.set_value('total_expense', frm.doc.additional_cost + frm.doc.total_manufacturing_expense + frm.doc.total_raw_material);
	}
	
	cur_frm.set_value('strapping_cost', frm.doc.strapping_cost_per_sqft * frm.doc.production_sqft);
	cur_frm.set_value('total_expense_per_sqft', (frm.doc.total_expense) / frm.doc.production_sqft);
	cur_frm.set_value('rack_shifting_total_expense1_per_sqft', (frm.doc.rack_shifting_total_expense1) / frm.doc.production_sqft);
	cur_frm.set_value('labour_expense', parseFloat(frm.doc.labour_cost_per_sqft) * parseFloat(frm.doc.production_sqft));
	cur_frm.set_value('item_price', frm.doc.total_expense_per_sqft + frm.doc.rack_shifting_total_expense1_per_sqft + frm.doc.labour_cost_per_sqft + frm.doc.shot_blast_per_sqft);
}
function std_item(frm) {
	if (frm.doc.bom_no) {
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.std_item",
			args: {
				doc: cur_frm.doc
			},
			callback(r) {
				// cur_frm.set_value('items',r.message)
				var item1 = []
				for (const d of r.message['items']) {
					// if(!item1.includes(d.item_code))
					item1.push('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))
				}
				for (const d of r.message['items']) {
					for (const i of frm.doc.items ? frm.doc.items : []) {
						if (i.item_code == d.item_code && d.layer_type == i.layer_type && item1.includes('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))) {
							item1.splice(item1.indexOf('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : '')), 1)
						}
					}
				}
				if (item1) {
					// for(var i=0;i<item1.length;i++){		
					for (const d of r.message['items']) {
						if (item1.includes('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))) {
							var row = frm.add_child('items');
							row.item_code = d.item_code;
							row.qty = d.qty;
							row.layer_type = 'Panmix'
							row.no_of_batches = frm.doc.bottom_layer_batches ? frm.doc.bottom_layer_batches : 0;
							row.ts_qty = d.qty;
							row.bom_qty = r.message['bom_qty'][d.item_code];
							row.average_consumption = d.average_consumption;
							row.stock_uom = d.stock_uom;
							row.from_usb = 1;
							row.uom = d.uom;
							if (d.rate == 0) {
								row.rate = d.validation_rate;
							}
							else {
								row.rate = d.rate;
							}
							row.amount = d.amount;
							row.source_warehouse = d.source_warehouse;
						}
						// }
					}
				}
				refresh_field("items");
				add_total_raw_material(cur_frm)
				frappe.call({
					method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.add_item",
					args: {
						bom_no: frm.doc.bom_no,
						doc: cur_frm.doc
					},
					callback(r) {
						// cur_frm.set_value('items',r.message)
						var item1 = []
						for (const d of r.message) {
							// if(!item1.includes(d.item_code))
							item1.push('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))
						}
						for (const d of r.message) {
							for (const i of frm.doc.items ? frm.doc.items : []) {
								if (i.item_code == d.item_code && d.layer_type == i.layer_type && item1.includes('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))) {
									item1.splice(item1.indexOf('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : '')), 1)
								}
							}
						}
						if (item1) {
							// for(var i=0;i<item1.length;i++){		
							for (const d of r.message) {
								if (item1.includes('item_code:' + (d.item_code ? d.item_code : '') + 'layer_type:' + (d.layer_type ? d.layer_type : ''))) {
									var row = frm.add_child('items');
									row.item_code = d.item_code;
									row.layer_type = d.layer_type
									row.qty = (d.layer_type == 'Top Layer' ? d.qty * (cur_frm.doc.total_no_of_batches ? cur_frm.doc.total_no_of_batches : 0) : d.qty);
									row.ts_qty = d.ts_qty;
									row.bom_qty = d.ts_qty;
									row.average_consumption = d.ts_qty;
									row.no_of_batches = frm.doc.total_no_of_batches
									row.stock_uom = d.stock_uom;
									row.from_bom = 1;
									row.uom = d.uom;
									row.rate = d.rate;
									row.amount = d.layer_type == 'Top Layer' ? d.amount * (cur_frm.doc.total_no_of_batches ? cur_frm.doc.total_no_of_batches : 0) : d.amount;
									row.source_warehouse = d.source_warehouse
								}
								// }
							}
						}
						refresh_field("items");
						add_total_raw_material(cur_frm)
					}
				})
			}
		})
	}

}
function default_value(usb_field, set_field) {
	frappe.db.get_single_value("USB Setting", usb_field).then(value => {
		cur_frm.set_value(set_field, value)
	})
	cur_frm.refresh_field(set_field);
}
frappe.ui.form.on('BOM Item', {
	rate: function (frm, cdt, cdn) {
		total_amount(frm, cdt, cdn)
		// frappe.model.set_value(cdt,cdn,"item_tax_template",r.message)
	},
	qty: function (frm, cdt, cdn) {
		total_amount(frm, cdt, cdn)
	},
	item_code: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.item_code) {
			frappe.call({
				method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.item_data",
				args: {
					item_code: d.item_code,
				},
				callback(r) {
					frappe.model.set_value(cdt, cdn, "rate", r.message[2])
					frappe.model.set_value(cdt, cdn, "uom", r.message[1])
					frappe.model.set_value(cdt, cdn, "stock_uom", r.message[1])
				}
			})
		}
		total_amount(frm, cdt, cdn)
	},
});
function total_amount(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", d.qty * d.rate)
}


function set_css(frm) {
	document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.color = 'white'
	document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.fontWeight = 'bold'
	document.querySelectorAll("[data-fieldname='curing_stock_entry']")[1].style.backgroundColor = '#3399ff'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.color = 'white'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.fontWeight = 'bold'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.backgroundColor = '#3399ff'
	document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.color = 'white'
	document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.fontWeight = 'bold'
	document.querySelectorAll("[data-fieldname='create_rack_shiftingstock_entry']")[1].style.backgroundColor = '#3399ff'
}

