# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json
from erpnext.stock.get_item_details import get_item_price
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils.data import nowdate
from ganapathy_pavers.utils.py.sitework_printformat import get_cw_monthly_cost
from ganapathy_pavers.custom.py.journal_entry import get_production_details
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_paver_production_report.itemwise_monthly_paver_production_report import get_production_cost, get_sqft_expense as paver_get_sqft_expense
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_cw_production_report.itemwise_monthly_cw_production_report import get_sqft_expense as cw_sqft_expense
import frappe
from frappe import _, scrub


def execute(filters=None):
	selling_price_lists = frappe.get_all("Price List", {"enabled": 1, "item_price_difference": 1}, pluck="name")
	columns = get_columns(filters.item, selling_price_lists)
	data = get_data(filters, selling_price_lists)
	return columns, data

def get_data(filters, selling_price_lists):
	item = filters.item
	if not item:
		return []

	item_dicts = []
	if frappe.db.get_value("Item", item, "has_variants"):
		variant_results = get_item_data(filters)
		if not variant_results:
			frappe.msgprint(_("There aren't any item variants for the selected item"))
			return []
	else:
		variant_results = frappe.get_all("Item", {"name": item})

	
	variant_list = [variant['name'] for variant in variant_results]

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
	paver_expense_cost=paver_get_sqft_expense(filters)
	cw_expense_cost={}
	prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=(filters.get("machine", []) or []))

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
				item_dict["production_rate"] += (paver_expense_cost /(prod_details.get("paver", 1) or 1)) 
		
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
			
			if exp_group not in cw_expense_cost:
				cw_expense_cost[exp_group] = cw_sqft_expense(filters, exp_group)

			item_dict["production_rate"] = get_cw_monthly_cost(filters=filters,
                                  _type=_type,
                                  exp_group=exp_group,
                                  prod=prod)
			if item_dict["production_rate"]:
				item_dict["production_rate"] += ((cw_expense_cost.get(exp_group, 0) or 0) /(prod_details.get(prod, 1) or 1))

		for price_list in selling_price_lists:
			selling_price_map = get_selling_price_map(filters, item_dict.get("variant_name"), price_list)
			item_dict[scrub(price_list)] = selling_price_map.get(name) or 0

		item_dicts.append(item_dict)

	return item_dicts

def get_columns(item, selling_price_lists):
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
		}
	]
	for price_list in selling_price_lists:
		additional_columns += [
		{
			"fieldname": scrub(price_list),
			"label": _(price_list),
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


def get_selling_price_map(filters, item, price_list):
	selling_price_map = {}
	args = {
	'item_code': item, 
		'price_list': price_list, 
		'uom': frappe.db.get_value("Item", item, "stock_uom"), 
		'transaction_date': None, 
		'posting_date': filters.get("to_date") or nowdate(), 
		'batch_no': None,
	}
	item_price=get_item_price(args=args, item_code=item)
	selling_price_map[item] = item_price[0][1] if len(item_price) and len(item_price[0])>1 else 0

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

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	conditions = []
	
	if isinstance(filters, str):
		filters = json.loads(filters)

	#Get searchfields from meta and use in Item Link field query
	meta = frappe.get_meta("Item", cached=True)
	searchfields = meta.get_search_fields()

	# these are handled separately
	ignored_search_fields = ("item_name", "description")
	for ignored_field in ignored_search_fields:
		if ignored_field in searchfields:
			searchfields.remove(ignored_field)

	columns = ''
	extra_searchfields = [field for field in searchfields
		if not field in ["name", "item_group", "description", "item_name"]]

	if extra_searchfields:
		columns = ", " + ", ".join(extra_searchfields)

	searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
		if not field in searchfields]
	searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

	if filters and isinstance(filters, dict):
		if filters.get('customer') or filters.get('supplier'):
			party = filters.get('customer') or filters.get('supplier')
			item_rules_list = frappe.get_all('Party Specific Item',
				filters = {'party': party}, fields = ['restrict_based_on', 'based_on_value'])

			filters_dict = {}
			for rule in item_rules_list:
				if rule['restrict_based_on'] == 'Item':
					rule['restrict_based_on'] = 'name'
				filters_dict[rule.restrict_based_on] = []

			for rule in item_rules_list:
				filters_dict[rule.restrict_based_on].append(rule.based_on_value)

			for filter in filters_dict:
				filters[scrub(filter)] = ['in', filters_dict[filter]]

			if filters.get('customer'):
				del filters['customer']
			else:
				del filters['supplier']
		else:
			filters.pop('customer', None)
			filters.pop('supplier', None)

	description_cond = ''
	if frappe.db.count('Item', cache=True) < 50000:
		# scan description only if items are less than 50000
		description_cond = 'or tabItem.description LIKE %(txt)s'
	return frappe.db.sql("""select
			tabItem.name, tabItem.item_name, tabItem.item_group,
		if(length(tabItem.description) > 40, \
			concat(substr(tabItem.description, 1, 40), "..."), description) as description
		{columns}
		from tabItem
		where tabItem.docstatus < 2
			and ((tabItem.has_variants = 1 and tabItem.item_group = 'Pavers') or (tabItem.item_group = 'Compound Walls'))
			and tabItem.disabled=0
			and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
			and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
				{description_cond})
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
			idx desc,
			name, item_name
		limit %(start)s, %(page_len)s """.format(
			columns=columns,
			scond=searchfields,
			fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
			mcond=get_match_cond(doctype).replace('%', '%%'),
			description_cond = description_cond),
			{
				"today": nowdate(),
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len
			}, as_dict=as_dict)