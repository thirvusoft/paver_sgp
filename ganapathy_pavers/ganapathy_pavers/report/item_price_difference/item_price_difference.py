# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json
from ganapathy_pavers.utils.py.sitework_printformat import get_cw_monthly_cost
from ganapathy_pavers.custom.py.journal_entry import get_production_details
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_paver_production_report.itemwise_monthly_paver_production_report import get_production_cost, get_sqft_expense
import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters.item)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	item = filters.item
	if not item:
		return []

	item_dicts = []

	variant_results = get_item_data(filters) 

	if not variant_results:
		frappe.msgprint(_("There aren't any item variants for the selected item"))
		return []
	else:
		variant_list = [variant['name'] for variant in variant_results]

	selling_price_map = get_selling_price_map(variant_list)
	attr_val_map = get_attribute_values_map(variant_list)

	attributes = frappe.db.get_all(
		"Item Variant Attribute",
		fields=["attribute"],
		filters={
			"parent": ["in", variant_list]
		},
		group_by="attribute"
	)
	attribute_list = [row.get("attribute") for row in attributes]

	# Prepare dicts
	expense_cost=get_sqft_expense(filters)
	prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=filters.get("machine", []))

	variant_dicts = [{"variant_name": d['name']} for d in variant_results]
	for item_dict in variant_dicts:
		name = item_dict.get("variant_name")

		for attribute in attribute_list:
			attr_dict = attr_val_map.get(name)
			if attr_dict and attr_dict.get(attribute):
				item_dict[frappe.scrub(attribute)] = attr_val_map.get(name).get(attribute)

		if frappe.db.get_value("Item", item_dict.get("variant_name"), "item_group") == "Pavers":
			item_dict["production_rate"] = sum(get_production_cost(filters, item_dict.get("variant_name"))) 
			if item_dict["production_rate"]:
				item_dict["production_rate"] += (expense_cost /(prod_details.get("paver", 1) or 1)) 
		
		if frappe.db.get_value("Item", item_dict.get("variant_name"), "item_group") == "Compound Walls":
			
			_type = [frappe.db.get_value("Item", item_dict.get("variant_name"), "compound_wall_type")]
			if "Post" in _type or "Slab" in _type:
				_type = ["Post", "Slab"]
			exp_group="cw_group"
			prod="cw"

			if _type == ["Lego Block"]:
				exp_group="lg_group"
				prod="lego"

			elif _type == ['Fencing Post']:
				exp_group="fp_group" 
				prod="fp"
			item_dict["production_rate"] = get_cw_monthly_cost(filters=filters,
                                  _type=_type,
                                  exp_group=exp_group,
                                  prod=prod)

		item_dict["selling_price_list_rate"] = selling_price_map.get(name) or 0

		item_dicts.append(item_dict)

	return item_dicts

def get_columns(item):
	columns = [{
		"fieldname": "variant_name",
		"label": "Variant",
		"fieldtype": "Link",
		"options": "Item",
		"width": 200
	}]

	item_doc = frappe.get_doc("Item", item)

	for entry in item_doc.attributes:
		columns.append({
			"fieldname": frappe.scrub(entry.attribute),
			"label": entry.attribute,
			"fieldtype": "Data",
			"width": 100
		})

	additional_columns = [
		{
			"fieldname": "production_rate",
			"label": _("Production Rate"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "avg_selling_price_list_rate",
			"label": _("Selling Price List Rate"),
			"fieldtype": "Currency",
			"width": 150
		}
	]
	columns.extend(additional_columns)

	return columns


def get_item_data(filters):
	item_doc = frappe.get_doc("Item", filters.item)

	attributes = {}

	for row in item_doc.attributes:
		attr = frappe.scrub(row.attribute)
		if attr in filters and filters.get(attr):
			attributes[attr] = filters.get(attr)

	result = []
	variants = frappe.db.get_all(
		"Item",
		fields=["name"],
		filters={
			"variant_of": ["=", filters.item],
			"disabled": 0
		},
	)

	for item in variants:
		item_doc = frappe.get_doc("Item", item.name)
		matches = []
		for attr in attributes:
			for row in item_doc.attributes:
				if (frappe.scrub(row.attribute) == attr and row.attribute_value in filters.get(attr)):
					matches.append(1)
					continue
		
		if len(matches) == len(attributes):
			result.append(item)

	return result


def get_selling_price_map(variant_list):
	selling = frappe.db.get_all(
		"Item Price",
		fields=[
			"avg(price_list_rate) as avg_rate",
			"item_code",
		],
		filters={
			"item_code": ["in", variant_list],
			"selling": 1
		},
		group_by="item_code"
	)

	selling_price_map = {}
	for row in selling:
		selling_price_map[row.get("item_code")] = row.get("avg_rate")

	return selling_price_map

def get_attribute_values_map(variant_list):
	attribute_list = frappe.db.get_all(
		"Item Variant Attribute",
		fields=[
			"attribute",
			"attribute_value",
			"parent"
		],
		filters={
			"parent": ["in", variant_list]
		}
	)

	attr_val_map = {}
	for row in attribute_list:
		name = row.get("parent")
		if not attr_val_map.get(name):
			attr_val_map[name] = {}

		attr_val_map[name][row.get("attribute")] = row.get("attribute_value")

	return attr_val_map
