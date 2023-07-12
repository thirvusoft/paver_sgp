// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shot Blast Costing', {
	onload: async function (frm) {
		frm.set_query("material_manufacturing", "items", function (f, cdt, cdn) {
			let data = locals[cdt][cdn]
			let args = {}
			if (data.item_name) {
				args["item_to_manufacture"] = data.item_name
			}
			args["is_shot_blasting"] = 1
			args["is_sample"] = 0
			args["docstatus"] = ["!=", 2]
			args["shot_blasted_bundle"] = [">", 0]
			if (frm.doc.to_time) {
				args["date"] = frm.doc.to_time
			}
			if (frm.doc.to_time) {
				args["warehouse"] = frm.doc.source_warehouse
			}

			return {
				query: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.material_manufacturing_query",
				filters: args
			}
		})
		frm.set_query("batch", "items", function (frm, cdt, cdn) {
			let row = locals[cdt][cdn]
			// if (!row.material_manufacturing) {
			// 	frappe.throw({ message: `Please Enter Paver Manufacturing at row ${row.idx}`, title: "Missing Fields", indicator: 'red' })
			// }
			return {
				query: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.batch_query",
				filters: {
					material_manufacturing: row.material_manufacturing,
					is_sample: 0
				}
			}
		})
		var mm_items = [];
		await frappe.db.get_list('Material Manufacturing', { filters: { is_shot_blasting: 1, docstatus: 0, is_sample: 0 }, fields: ['item_to_manufacture'], limit: 0 }).then((value) => {
			for (let i = 0; i < value.length; i++) {
				if (!(mm_items.includes(value[i].item_to_manufacture))) {
					mm_items.push(value[i].item_to_manufacture)
				}
			}
		})
		frm.set_query("item_name", "items", function () {
			return {
				filters: {
					item_code: ['in', mm_items]
				}
			}
		})
	},
	create_stock_entry: function (frm) {
		make_stock_entry(frm)
	},
	setup: function (frm) {
		if (cur_frm.is_new() == 1) {
			frappe.db.get_single_value("USB Setting", "default_shot_blast_workstation").then(value => {
				cur_frm.set_value("workstation", value)
			})
			cur_frm.refresh_field("workstation");
			frm.trigger('fetch_warehouse_from_workstation');
		}
	},
	fetch_warehouse_from_workstation: function (frm) {
		if (frm.doc.workstation) {
			frappe.db.get_value("Workstation", frm.doc.workstation, "default_curing_target_warehouse").then(value => {
				cur_frm.set_value("warehouse", value['message']['default_curing_target_warehouse'])
			})
			cur_frm.refresh_field("warehouse");

			frappe.db.get_value("Workstation", frm.doc.workstation, "default_curing_target_warehouse_for_setting").then(value => {
				cur_frm.set_value("source_warehouse", value['message']['default_curing_target_warehouse_for_setting'])
			})
			cur_frm.refresh_field("source_warehouse");
		}
	},
	validate: function (frm) {
		frm.trigger("total_cost")
		total(frm)
		total_damage_cost(frm)
	},
	no_of_labour: function (frm) {
		total_cost(frm)
	},
	workstation: function (frm) {
		frm.trigger('fetch_warehouse_from_workstation');
		if (cur_frm.doc.workstation) {
			frappe.db.get_value('Workstation', cur_frm.doc.workstation, 'no_of_labours').then(value => {
				cur_frm.set_value('no_of_labour', value.message.no_of_labours)
			})
		} else {
			cur_frm.set_value('no_of_labour', 0)
		}
		frm.trigger("get_operators");
	},
	total_cost: function (frm) {
		cur_frm.set_value("total_cost_per_sqft", frm.doc.total_cost / (frm.doc.total_sqft - frm.doc.total_damage_sqft))
	},
	from_time: function (frm) {
		var field = "total_hrs"
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to_time)
	},
	update_batch_stock_qty: function (frm) {
		frm.doc.items.forEach(async row => {
			await frappe.call({
				method: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.uom_conversion",
				args: {
					batch: row.batch,
					mm: row.material_manufacturing,
					date: frm.doc.to_time,
					warehouse: frm.doc.source_warehouse
				},
				callback(r) {
					frappe.model.set_value(row.doctype, row.name, 'bdl', r.message["bundle"] || 0);
					frappe.model.set_value(row.doctype, row.name, 'batch_stock', r.message["stock"] || 0);
					cur_frm.refresh_field('items')

				}
			})
		})
	},
	to_time: async function (frm) {
		var field = "total_hrs"
		frm.trigger("update_batch_stock_qty")
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to_time)
	},
	total_hrs: function (frm) {
		total_cost(frm)
	},
	additional_cost: function (frm) {
		cur_frm.set_value('total_cost', frm.doc.additional_cost + frm.doc.labour_cost)
	},
	labour_cost: function (frm) {
		cur_frm.set_value('total_cost', frm.doc.additional_cost + frm.doc.labour_cost)
	},
	get_operators: function (frm) {
		if (frm.doc.workstation) {
			frappe.call({
				method: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.get_operators",
				args: {
					workstation: frm.doc.workstation || '',
					division: frm.doc.division || 1,
				},
				callback: function (r) {
					frm.set_value("operator_details", r.message);
					var total_operator_wages = 0;
					for (let row = 0; row < r.message.length; row++) {
						total_operator_wages += r.message[row].division_salary;
					}
					frm.set_value("total_operator_wages", total_operator_wages);
				},
			});
		} else {
			frm.set_value("operator_details", []);
			frm.set_value("total_operator_wages", 0);
		}
	},
	division: function (frm) {
		let operator_details = frm.doc.operator_details ? frm.doc.operator_details : [],
			total_operator_wages = 0;
		for (let row = 0; row < operator_details.length; row++) {
			let cdt = operator_details[row].doctype,
				cdn = operator_details[row].name;
			let data = locals[cdt][cdn];
			let wages = (data.salary ? data.salary : 0) / (frm.doc.division ? frm.doc.division : 1);
			frappe.model.set_value(cdt, cdn, "division_salary", wages);
			total_operator_wages += wages;
		}
		frm.set_value("total_operator_wages", total_operator_wages);
	},
});
frappe.ui.form.on('Shot Blast Items', {
	material_manufacturing: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if (!row.material_manufacturing) {
			return
		}
		frappe.db.get_doc("Material Manufacturing", row.material_manufacturing).then(async (r) => {
			frappe.model.set_value(cdt, cdn, "item_name", r.item_to_manufacture)
			frappe.model.set_value(cdt, cdn, "batch", r.batch_no_curing)
		});
	},
	damages_in_nos: async function (frm, cdt, cdn) {
		total_damage_cost(frm)
		var row = locals[cdt][cdn]
		let sqft = await ganapathy_pavers.uom_conversion(row.item_name, 'Nos', row.damages_in_nos, 'SQF')
		frappe.model.set_value(cdt, cdn, "damages_in_sqft", sqft)
	},
	bundle_taken: async function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if (row.bundle_taken > (row.bdl || 0)) {
			frappe.model.set_value(cdt, cdn, "bundle_taken", 0)
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
		let sqft = await ganapathy_pavers.uom_conversion(row.item_name, 'Bdl', row.bundle_taken, 'SQF')
		let sqft_pieces = await ganapathy_pavers.uom_conversion(row.item_name, 'Nos', row.taken_pieces, 'SQF')
		frappe.model.set_value(cdt, cdn, "sqft", (sqft || 0) + (sqft_pieces || 0))
	},
	taken_pieces: async function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if (row.bundle_taken > (row.bdl || 0)) {
			frappe.model.set_value(cdt, cdn, "bundle_taken", 0)
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
		let sqft = await ganapathy_pavers.uom_conversion(row.item_name, 'Bdl', row.bundle_taken, 'SQF')
		let sqft_pieces = await ganapathy_pavers.uom_conversion(row.item_name, 'Nos', row.taken_pieces, 'SQF')
		frappe.model.set_value(cdt, cdn, "sqft", (sqft || 0) + (sqft_pieces || 0))
	},
	sqft: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		total(frm)
	},
	damages_in_sqft: function (frm, cdt, cdn) {
		total_damage_cost(frm)
		var total_damage_sqft = 0
		for (var i = 0; i < frm.doc.items.length; i++) {
			total_damage_sqft += frm.doc.items[i].damages_in_sqft
		}
		cur_frm.set_value("total_damage_sqft", total_damage_sqft)
		cur_frm.set_value("avg_damage_sqft", total_damage_sqft / frm.doc.items.length)
	},
	batch: async function (frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.batch) {
			let batch = await frappe.db.get_value("Batch", row.batch, "item")
			frappe.model.set_value(cdt, cdn, "item_name", batch.message.item)
		}
		if (!row.material_manufacturing) {
			frappe.show_alert({ message: `Kindly enter <b>Paver Manufacturing</b> at row ${row.idx}`, indicator: "red" })
			return
		}
		frappe.call({
			method: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.uom_conversion",
			args: {
				batch: row.batch,
				mm: row.material_manufacturing,
				date: frm.doc.to_time,
				warehouse: frm.doc.source_warehouse
			},
			callback(r) {
				frappe.model.set_value(row.doctype, row.name, 'bdl', r.message["bundle"] || 0);
				frappe.model.set_value(row.doctype, row.name, 'batch_stock', r.message["stock"] || 0);
				cur_frm.refresh_field('items')

			}
		})

	}
});
function total(frm) {
	var total_bundle = 0
	var total_pieces = 0
	var total_sqft = 0
	for (var i = 0; i < (frm.doc.items || []).length; i++) {
		total_bundle += frm.doc.items[i].bundle_taken || 0
		total_sqft += frm.doc.items[i].sqft || 0
		total_pieces += frm.doc.items[i].taken_pieces || 0

		if (frm.doc.items[i].bundle_taken > frm.doc.items[i].bdl) {
			frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "bundle_taken", 0)
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
	}
	cur_frm.set_value("total_bundle", total_bundle)
	cur_frm.set_value("total_sqft", total_sqft)
	cur_frm.set_value("total_pieces", total_pieces)
}
function total_hrs(frm, field, from, to) {
	frappe.call({
		method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.total_hrs",
		args: {
			from_time: from,
			to: to
		},
		callback(r) {
			cur_frm.set_value(field, r.message);
		}
	})
}
function total_cost(frm) {
	if (frm.doc.docstatus == 0) {
		cur_frm.set_value('labour_cost', frm.doc.labour_cost_in_workstation * frm.doc.total_hrs * frm.doc.no_of_labour);
		cur_frm.set_value('total_cost', (frm.doc.additional_cost || 0) + (frm.doc.labour_cost || 0) + (frm.doc.total_operator_wages || 0));
	}
}
frappe.ui.form.on('Shot Blast Costing', {
	refresh: function (frm) {
		set_css(frm);
	},
});
function set_css(frm) {
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.color = 'white'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.fontWeight = 'bold'
	document.querySelectorAll("[data-fieldname='create_stock_entry']")[1].style.backgroundColor = '#3399ff'
}
function make_stock_entry(frm, type) {
	frappe.call({
		method: "ganapathy_pavers.ganapathy_pavers.doctype.shot_blast_costing.shot_blast_costing.make_stock_entry",
		args: {
			doc: frm.doc
		},
	})
}

async function total_damage_cost(frm) {
	await frappe.call({
		method: "run_doc_method",
		args: {
			'docs': frm.doc,
			'method': 'calculate_total_damage_cost'
		},
		callback: function (r) {
			if (!r.exc) {
				frm.refresh_fields();
			}
		}
	});
}
