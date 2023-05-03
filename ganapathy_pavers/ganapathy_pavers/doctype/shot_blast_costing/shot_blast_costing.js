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
			args["docstatus"] = ["!=", 2]
			args["shot_blasted_bundle"] = [">", 0]
			if (frm.doc.to_time){
				args["date"] = frm.doc.to_time
			}
			if (frm.doc.to_time){
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
					material_manufacturing: row.material_manufacturing
				}
			}
		})
		var mm_items = [];
		await frappe.db.get_list('Material Manufacturing', { filters: { is_shot_blasting: 1, docstatus: 0 }, fields: ['item_to_manufacture'] }).then((value) => {
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
			frappe.db.get_single_value("USB Setting", "default_curing_target_warehouse").then(value => {
				cur_frm.set_value("warehouse", value)
			})
			cur_frm.refresh_field("warehouse");
			frappe.db.get_single_value("USB Setting", "default_curing_target_warehouse_for_setting").then(value => {
				cur_frm.set_value("source_warehouse", value)
			})
			cur_frm.refresh_field("source_warehouse");
			frappe.db.get_single_value("USB Setting", "default_shot_blast_workstation").then(value => {
				cur_frm.set_value("workstation", value)
			})
			cur_frm.refresh_field("workstation");
		}
	},
	validate: function (frm) {
		total(frm)
	},
	no_of_labour: function (frm) {
		total_cost(frm)
	},
	workstation: function (frm) {
		if (cur_frm.doc.workstation) {
			frappe.db.get_value('Workstation', cur_frm.doc.workstation, 'no_of_labours').then(value => {
				cur_frm.set_value('no_of_labour', value.message.no_of_labours)
			})
		} else {
			cur_frm.set_value('no_of_labour', 0)
		}
	},
	total_cost: function (frm) {
		cur_frm.set_value("total_cost_per_sqft", frm.doc.total_cost / frm.doc.total_sqft)
	},
	from_time: function (frm) {
		var field = "total_hrs"
		total_hrs(frm, field, frm.doc.from_time, frm.doc.to_time)
	},
	to_time: function (frm) {
		var field = "total_hrs"
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
		var row = locals[cdt][cdn]
		let sqft = await ganapathy_pavers.uom_converstion(row.item_name, 'Nos', row.damages_in_nos, 'SQF')
		frappe.model.set_value(cdt, cdn, "damages_in_sqft", sqft)
	},
	bundle_taken: async function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if (row.bundle_taken > (row.bdl || 0)) {
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
		let sqft = await ganapathy_pavers.uom_converstion(row.item_name, 'Bdl', row.bundle_taken, 'SQF')
		let sqft_pieces = await ganapathy_pavers.uom_converstion(row.item_name, 'Nos', row.taken_pieces, 'SQF')
		frappe.model.set_value(cdt, cdn, "sqft", (sqft || 0) + (sqft_pieces || 0))
	},
	taken_pieces: async function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if (row.bundle_taken > (row.bdl || 0)) {
			frappe.throw("Taken Bundle is Greater Than Produced Bundle")
		}
		let sqft = await ganapathy_pavers.uom_converstion(row.item_name, 'Bdl', row.bundle_taken, 'SQF')
		let sqft_pieces = await ganapathy_pavers.uom_converstion(row.item_name, 'Nos', row.taken_pieces, 'SQF')
		frappe.model.set_value(cdt, cdn, "sqft", (sqft || 0) + (sqft_pieces || 0))
	},
	sqft: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		total(frm)
	},
	damages_in_sqft: function (frm, cdt, cdn) {
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
				mm: row.material_manufacturing
			},
			callback(r) {
				frappe.model.set_value(row.doctype, row.name, 'bdl', r.message || 0);
				cur_frm.refresh_field('items')

			}
		})

	}
});
function total(frm) {
	var total_bundle = 0
	var total_pieces = 0
	var total_sqft = 0
	for (var i = 0; i < frm.doc.items.length; i++) {
		total_bundle += frm.doc.items[i].bundle_taken || 0
		total_sqft += frm.doc.items[i].sqft || 0
		total_pieces += frm.doc.items[i].taken_pieces || 0

		if (frm.doc.items[i].bundle_taken > frm.doc.items[i].bdl) {
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
	if (frm.doc.total_hrs && frm.doc.docstatus == 0) {
		cur_frm.set_value('labour_cost', frm.doc.labour_cost_in_workstation * frm.doc.total_hrs * frm.doc.no_of_labour);
		cur_frm.set_value('total_cost', frm.doc.additional_cost + frm.doc.labour_cost);
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