import copy
from ganapathy_pavers.custom.py.journal_entry import get_production_details
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_paver_production_report.itemwise_monthly_paver_production_report import get_production_cost
import frappe
from frappe.utils import nowdate, get_first_day, get_last_day
from ganapathy_pavers import uom_conversion
from erpnext.stock.get_item_details import get_item_price
from ganapathy_pavers.custom.py.expense import total_expense

DATE_FORMAT = "%Y-%m-%d"

def site_work(doc):
	doc=frappe.get_doc("Project",doc)
	items={}
	exp={}
	production_rate={}
	without_transport_cost=doc.total
	nos=0
	supply_sqf=0
	sqf=doc.measurement_sqft or 0
	dn=frappe.get_all("Delivery Note", {"site_work": doc.name, "docstatus": 1}, pluck="name")
	si=frappe.get_all("Sales Invoice", {"site_work": doc.name, "docstatus": 1, "update_stock": 1}, pluck="name")
	for i in doc.delivery_detail:
		rate=0
		for item_row in (doc.item_details or []) + (doc.item_details_compound_wall or []) + (doc.raw_material or []):
			if item_row.get("item")==i.item:
				rate=item_row.get('rate', 0)
		if not rate:
			rate_list=frappe.db.sql(f"""
				select dni.rate
				from `tabDelivery Note Item` as dni left outer join `tabDelivery Note` as dn
					on dni.parent = dn.name
				where dn.site_work='{doc.name}' and dni.item_code='{i.item}'
			""")
			if rate_list and rate_list[0] and rate_list[0][0]:
				rate=rate_list[0][0]
		if i.item not in items:
			items[i.item]={
				"nos":0,"sqf":0,"rate": rate,
			}
		items[i.item]["nos"]+=round(uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),'Nos'),2)
		nos+=uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"Nos")
		items[i.item]["sqf"]+=round(uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"SQF"),2)
		supply_sqf+=uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"SQF")
	
	_items = copy.deepcopy(items)
	for row in _items:
		if not _items[row].get('nos') and not _items[row].get('sqf'):
			del items[row]

	for row in doc.additional_cost:
		if row.description.lower().strip() not in exp:
			exp[row.description.lower().strip()]={"description": row.description, "nos": row.nos, "amount": row.amount, "sqft_amount": (row.amount or 0)/sqf if sqf else 0, "supply_sqft_amount": (row.amount or 0)/supply_sqf if supply_sqf else 0}
		else:
			exp[row.description.lower().strip()]["nos"]+=row.nos
			exp[row.description.lower().strip()]["amount"]+=row.amount
			exp[row.description.lower().strip()]["sqft_amount"]+=(row.amount or 0)/sqf if sqf else 0
			exp[row.description.lower().strip()]["supply_sqft_amount"]+=(row.amount or 0)/supply_sqf if supply_sqf else 0
	
	for i in list(exp.values()):
		if "transport" in i["description"].lower():
			without_transport_cost -= i["amount"]
		
		if 'fastag' in i["description"].lower():
			doc.total -= i['amount'] or 0
			without_transport_cost -= i["amount"]
			# doc.transporting_cost += i['amount'] or 0

	delivered_items=(items.keys())
	dn_items=frappe.get_all("Delivery Note Item", {"parenttype": "Delivery Note", "parent": ["in", dn], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
	dn_items+=frappe.get_all("Sales Invoice Item", {"parenttype": "Sales Invoice", "parent": ["in", si], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
	
	paver_prod_details = []
	for item in dn_items:
		if item['item_code'] not in production_rate:
			production_rate[item['item_code']] = []
		
		if [item["item_code"], get_first_day(item["creation"])] not in paver_prod_details:
			prod_cost=get_item_price_list_rate(item["item_code"], item["creation"])
			paver_prod_details.append([item["item_code"], get_first_day(item["creation"])])
			if prod_cost:
				production_rate[item['item_code']].append(prod_cost)
		
	for item in production_rate:
		if isinstance(production_rate[item], list):
			if len(list(set(production_rate[item]))):
				production_rate[item]= sum(list(set(production_rate[item])))/len(list(set(production_rate[item])))

	total_job_worker_cost = sum([(i.amount or 0) for i in doc.job_worker if not i.other_work])
	total_other_worker_cost = sum([(i.amount or 0) for i in doc.job_worker if i.other_work])
	
	return {
			'items':items,
			'nos':round(nos,2),
			'sqf':round(sqf,2), 
			'expense': list(exp.values()), 
			'own_vehicle_cost': doc.transporting_cost,
			'transporting_cost': (doc.transporting_cost + (doc.total - without_transport_cost)) / sqf if sqf else 0,
			'supply_transporting_cost': (doc.transporting_cost + (doc.total - without_transport_cost)) / supply_sqf if supply_sqf else 0,
			'total_job_worker_cost': total_job_worker_cost / sqf if sqf else 0,
			'total_other_worker_cost': total_other_worker_cost / sqf if sqf else 0,
			'supply_total_job_worker_cost': total_job_worker_cost / supply_sqf if supply_sqf else 0,
			'supply_total_other_worker_cost': total_other_worker_cost / supply_sqf if supply_sqf else 0,
			'total': without_transport_cost / sqf if sqf else 0, 
			'supply_total': without_transport_cost / supply_sqf if supply_sqf else 0,
			'supply_sqf': supply_sqf, 
			'production_rate': production_rate
		}
	

def site_completion_delivery_uom(site_work, item_group='Raw Material'):
	query=f"""
		SELECT 
			dni.item_code,
			dn.posting_date as date,
			SUM(dni.qty) as qty,
			dni.uom,
			AVG(dni.rate) as rate,
			SUM(dni.amount) as amount,
			CASE
				WHEN IFNULL((
						select 
							rm.is_supplied_rate
						from `tabRaw Materials` rm
						where 
							rm.item= dni.item_code and
							rm.parenttype="Project" and
							rm.parent='{site_work}' and
							rm.is_supplied_rate = 1
						limit 1
						), 0) = 1
					THEN IFNULL((
						select 
							rm.rate /
							ifnull((
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=rm.item and
									uom.uom=rm.uom
								limit 1
								), 0)
						from `tabRaw Materials` rm
						where 
							rm.item= dni.item_code and
							rm.parenttype="Project" and
							rm.parent='{site_work}' and
							rm.is_supplied_rate = 1
						limit 1
						), 0)*
						ifnull((
							SELECT
								uom.conversion_factor
							FROM `tabUOM Conversion Detail` uom
							WHERE
								uom.parenttype='Item' and
								uom.parent=dni.item_code and
								uom.uom=dni.uom
							limit 1
						)    
						, 0)
				ELSE ROUND(
					ifnull((
						SELECT sle.incoming_rate + (sle.incoming_rate /100 * IFNULL(
							(
								SELECT
									sle_pi.taxes_and_charges_added * 100 / sle_pi.total
								FROM `tabPurchase Invoice` sle_pi
								WHERE
									sle_pi.name = sle.voucher_no
								LIMIT 1
							), 0))
						FROM `tabStock Ledger Entry` sle
						WHERE
							sle.is_cancelled=0 and
							sle.voucher_type = 'Purchase Invoice' and
							sle.item_code = dni.item_code and
							sle.posting_date  <= dn.posting_date and
							sle.is_cancelled = 0 and
							sle.project='{site_work}'
						order by posting_date desc
						limit 1
					), ifnull(
								((
								select 
									avg(rm.rate) /
									ifnull(
										ifnull(
											(
												SELECT
													pi_item.conversion_factor
												FROM `tabPurchase Invoice Item` pi_item
												WHERE 
													pi_item.name = (
															SELECT 
																sle.voucher_detail_no 
															FROM `tabStock Ledger Entry` sle 
															WHERE
																sle.is_cancelled=0 and
																sle.voucher_type = 'Purchase Invoice' and
																sle.item_code = dni.item_code and
																sle.posting_date  <= dn.posting_date and
																sle.is_cancelled = 0 and
																sle.project='{site_work}'
															order by posting_date desc
															limit 1
														) and
													pi_item.uom = rm.uom
											),
											(
												SELECT
													uom.conversion_factor
												FROM `tabUOM Conversion Detail` uom
												WHERE
													uom.parenttype='Item' and
													uom.parent=rm.item and
													uom.uom=rm.uom
												limit 1
											)
										), 0
									)
								from `tabRaw Materials` rm
								where 
									rm.item= dni.item_code and
									rm.parenttype="Project" and
									rm.parent='{site_work}'
								)
							))) *
					ifnull(
						ifnull(
							(
								SELECT
									pi_item.conversion_factor
								FROM `tabPurchase Invoice Item` pi_item
								WHERE 
									pi_item.name = (
											SELECT 
												sle.voucher_detail_no 
											FROM `tabStock Ledger Entry` sle 
											WHERE
												sle.is_cancelled=0 and
												sle.voucher_type = 'Purchase Invoice' and
												sle.item_code = dni.item_code and
												sle.posting_date  <= dn.posting_date and
												sle.is_cancelled = 0 and
												sle.project='{site_work}'
											order by posting_date desc
											limit 1
										) and
									pi_item.uom = dni.uom
							),
							(
								SELECT
									uom.conversion_factor
								FROM `tabUOM Conversion Detail` uom
								WHERE
									uom.parenttype='Item' and
									uom.parent=dni.item_code and
									uom.uom=dni.uom
								limit 1
							)
						), 0
					)
				, 2) 
			END as valuation_rate
		FROM `tabDelivery Note Item` dni
		LEFT OUTER JOIN `tabDelivery Note` dn
		ON dn.name=dni.parent AND dni.parenttype="Delivery Note"
		WHERE
			dni.item_group='{item_group}'
			AND dn.site_work='{site_work}'
			AND dn.docstatus=1
		GROUP BY dni.item_code, dni.uom
	"""
	res = frappe.db.sql(query, as_dict=True)
	frappe.log_error(title='res', message=res)
	res+=frappe.db.sql(f""" 
		select
			child.item_code,
			SUM(child.qty) as qty,
			child.uom,
			AVG(child.rate) as rate,
			AVG(child.rate) as valuation_rate,
			SUM(child.amount) as amount
		from `tabPurchase Order` as doc
		left outer join `tabPurchase Order Item` as child
			on doc.name = child.parent
		where 
			doc.docstatus = 1 
			and doc.site_work = '{site_work}' 
			and child.delivered_by_supplier = 1
		group by 
			child.item_code, 
			child.uom
		""", as_dict=True)
	frappe.log_error(title='res', message=res)
	f_res = {}

	for row in res:
		if row.item_code not in f_res:
			f_res[row.item_code] = []
		f_res[row.item_code].append(row)
	
	customer_scope_qty = {}
	s_orders = frappe.get_all('Sales Order', {'docstatus': 1, 'site_work': site_work})
	for so in s_orders:
		so = frappe.get_doc('Sales Order', so)
		for row in so.items:
			if row.item_group == 'Raw Material' and row.customer_scope:
				if row.item_code not in customer_scope_qty:
					customer_scope_qty[row.item_code] = 0
				
				customer_scope_qty[row.item_code] += (row.qty or 0)

	return {
			'delivery_detail': f_res,
			'customer_scope_qty': customer_scope_qty
		}

def get_item_price_list_rate(item, date):
	price_list=frappe.db.get_value("Price List", {"site_work_print_format": 1, "selling": 1}, "name")
	if not price_list:
		return 0
	args = {
	'item_code': item, 
		'price_list': price_list, 
		'uom': frappe.db.get_value("Item", item, "stock_uom"), 
		'transaction_date': None, 
		'posting_date': date or nowdate(), 
		'batch_no': None,
	}
	item_price=get_item_price(args=args, item_code=item)
	return item_price[0][1] if len(item_price) and len(item_price[0])>1 else 0

def get_paver_production_rate(item, date=None, machine=[], include_sample_rate=False, include_expense = False):
	def get_paver_production_date(filters, item):
		if frappe.get_all("Material Manufacturing", {
			"item_to_manufacture": item,
			"docstatus": ["!=", 2],
			"is_sample": 0,
			"from_time": ["between", [filters.get('from_date'), filters.get('to_date')]]
			}):
			return filters
		
		date = frappe.get_all("Material Manufacturing",{
			"item_to_manufacture": item,
			"docstatus": ["!=", 2],
			"is_sample": 0,
			"from_time": ["<=", filters.get('to_date'),]
			}, order_by="from_time desc", pluck="from_time", limit=1)

		if not date:
			date = frappe.get_all("Material Manufacturing",{
			"item_to_manufacture": item,
			"docstatus": ["!=", 2],
			"is_sample": 0,
			}, order_by="from_time desc", pluck="from_time", limit=1)
		
		if not date:
			return filters
	
		filters["from_date"] = get_first_day(date[0]).strftime(DATE_FORMAT)
		filters["last_date"] = get_last_day(date[0]).strftime(DATE_FORMAT)
		return filters
	

	if not date:
		date=nowdate()
	
	filters = {
		"from_date": get_first_day(date).strftime(DATE_FORMAT),
		"to_date": get_last_day(date).strftime(DATE_FORMAT),
		"machine": machine
	}
	filters = get_paver_production_date(filters, item)
	
	expense_rate = 0
	if include_expense:
		prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=machine, item=filters.get("item"))
		expense_rate = total_expense(
                    from_date=filters.get('from_date'),
                    to_date=filters.get('to_date'),
                    prod_details="Paver",
                    expense_type="Manufacturing",
                    machine = machine,
                ) 
		expense_rate /= (prod_details.get('paver') or 1)

	return expense_rate+sum(get_production_cost(filters, item, include_sample_rate=include_sample_rate))

def get_cw_production_rate(_type=[], date=None):
	def get_cw_production_date(_type, filters):
		if frappe.get_all("CW Manufacturing", {
			"docstatus": ["!=", 2],
			"type": ["in", _type], 
			"molding_date": ["between", [filters.get('from_date'), filters.get('to_date')]]
			}):
			return filters
		
		date = frappe.get_all("CW Manufacturing",{
			"docstatus": ["!=", 2],
			"type": ["in", _type], 
			"molding_date": ["<=", filters.get('to_date'),]
			}, order_by="molding_date desc", pluck="molding_date", limit=1)

		if not date:
			date = frappe.get_all("CW Manufacturing",{
			"docstatus": ["!=", 2],
			"type": ["in", _type], 
			}, order_by="molding_date desc", pluck="molding_date", limit=1)
		
		if not date:
			return filters
	
		filters["from_date"] = get_first_day(date[0]).strftime(DATE_FORMAT)
		filters["to_date"] = get_last_day(date[0]).strftime(DATE_FORMAT)
		return filters
	

	if not date:
		date=nowdate()
	
	filters = {
		"from_date": get_first_day(date).strftime(DATE_FORMAT),
		"to_date": get_last_day(date).strftime(DATE_FORMAT),
	}

	filters = get_cw_production_date(_type, filters)
	cw_cost = sum(get_cw_monthly_cost(filters=filters, _type=_type))

	return cw_cost

def get_cw_monthly_cost(filters=None, _type=[], sub_type=[]):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	type_wise_subtype = {
		cw: frappe.db.get_all("Compound Wall Sub Type", {'compound_wall_type': cw, 'name': ['in', sub_type]}, pluck="name")
		for cw in (_type if isinstance(_type, (list, tuple)) else [_type])
	}

	cw_list = []
	if type_wise_subtype:
		for _type in type_wise_subtype:
			filters = {'molding_date':["between",[from_date,to_date]],'type': _type}
			if type_wise_subtype[_type]:
				filters['sub_type'] = ["in", type_wise_subtype[_type]]

			cw_list += frappe.db.get_list("CW Manufacturing",filters=filters,pluck="name")
	else:
		filters = {'molding_date':["between",[from_date,to_date]]}
		cw_list = frappe.db.get_list("CW Manufacturing",filters=filters,pluck="name")

	total_cost_per_sqft = 0
	rm_cost = 0

	if cw_list:
		bom_item = frappe.db.sql(""" 
								select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent {0} group by item_code """.format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_list=1)
		production_qty = frappe.db.sql(""" 
								select sum(production_sqft) as production_sqft,
								avg(total_cost_per_sqft) as total_cost_per_sqft,
								sum(total_expence) as total_expence,
								sum(raw_material_cost) as raw_material_cost,
								sum(total_expense_for_unmolding) as total_expense_for_unmolding,
								sum(labour_expense_for_curing) as total_expense_for_curing,
								AVG(total_labour_wages + labour_expense_for_curing)/AVG(production_sqft) as labour_cost_per_sqft,
								AVG(total_operator_wages)/AVG(production_sqft) as operator_cost_per_sqft,
								avg(strapping_cost_per_sqft) as strapping_cost_per_sqft,
								avg(additional_cost_per_sqft) as additional_cost_per_sqft,
								avg(raw_material_cost_per_sqft) as raw_material_cost_per_sqft from `tabCW Manufacturing` where name {0}""".format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_dict=1)
		
		for item in bom_item:
			rm_cost += item[4] / (production_qty[0]['production_sqft'] or 1)

		total_cost_per_sqft +=  ((production_qty[0]['strapping_cost_per_sqft'] or 0)
								+ (production_qty[0]['additional_cost_per_sqft']  or 0)
								+ (production_qty[0]["labour_cost_per_sqft"] or 0) 
								+ (production_qty[0]['operator_cost_per_sqft'] or 0))
	return rm_cost, total_cost_per_sqft

def get_delivery_transport_detail(sitename):
	conv_query = """
	ifnull((
		SELECT
			uom.conversion_factor
		FROM `tabUOM Conversion Detail` uom
		WHERE
			uom.parenttype='Item' and
			uom.parent=dni.item_code and
			uom.uom=dni.uom
	)
	, 0)/
	ifnull((
		SELECT
			uom.conversion_factor
		FROM `tabUOM Conversion Detail` uom
		WHERE
			uom.parenttype='Item' and
			uom.parent=dni.item_code and
			uom.uom='SQF'
	)    
	, 0)
	"""
	query = f"""
		select
			sum(
				(case
					when ifnull(dn.own_vehicle_no, '')!='' 
						then dni.qty
					else
						0
				end)
				*{conv_query}
				) as own_vehicle,
			sum(
				(case
					when ifnull(dn.own_vehicle_no, '')='' and ifnull(dn.vehicle_no, '')!=''
						then dni.qty
					else
						0
				end)
				*{conv_query}
				) as rental_vehicle,

			sum(
				(case
					when ifnull(dn.own_vehicle_no, '')!='' and ifnull(dn.is_customer_scope_expense, '') != 'Yes'
						then dni.qty
					else
						0
				end)
				*{conv_query}
				) as own_vehicle_without_cs,
			sum(
				(case
					when ifnull(dn.own_vehicle_no, '')='' and ifnull(dn.vehicle_no, '')!='' and ifnull(dn.is_customer_scope_expense, '') != 'Yes'
						then dni.qty
					else
						0
				end)
				*{conv_query}
				) as rental_vehicle_without_cs
				
		from `tabDelivery Note Item` dni
		inner join `tabDelivery Note` dn
		on dni.parenttype='Delivery Note' and dni.parent=dn.name
		where
			dni.item_group in ("Pavers", "Compound Walls") and
			dn.docstatus=1 and
			dn.site_work='{sitename}'
	"""

	res = frappe.db.sql(query, as_dict=True)
	return res[0] if res and res[0] else {}

def get_retail_cost(doc):
	doc=frappe.get_doc("Project",doc)
	rental_cost, rental_cost_without_cs = 0, 0
	unrelated_other_sqft, unrelated_other_sqft_without_cs = 0, 0
	unrelated_other_per_sqft, unrelated_other_sqft_without_cs =0, 0
	add_cost, add_cost_without_cs = 0, 0
	for i in doc.additional_cost:

		if "transport" in i.description.lower():
			rental_cost += i.amount or 0
			if i.is_customer_scope_expense != 'Yes':
				rental_cost_without_cs += i.amount or 0
		elif 'fastag' in i.description.lower():
			pass
		else:
			add_cost += i.amount or 0
			if i.is_customer_scope_expense != 'Yes':
				add_cost_without_cs += i.amount or 0
			
	other_cost, other_cost_without_cs = 0, 0
	job_work_cost, job_work_cost_without_cs = {}, {}
	unrelated_other_cost, unrelated_other_cost_without_cs = 0, 0
	jw_amt, jw_amt_without_cs = 0, 0
	jw_rate, jw_rate_without_cs = [], []
	for m in doc.job_worker:
		if m.other_work == 1:
			if not m.related_work:
				unrelated_other_sqft += (m.sqft_allocated or 0) if not m.amount_calc_by_person else 0
				unrelated_other_cost += m.amount or 0

				if m.is_customer_scope_expense != 'Yes':
					unrelated_other_sqft_without_cs += (m.sqft_allocated or 0) if not m.amount_calc_by_person else 0
					unrelated_other_cost_without_cs += m.amount or 0

			else:
				other_cost+= m.amount or 0
				if m.is_customer_scope_expense != 'Yes':
					other_cost_without_cs +=  m.amount or 0
		else:
			if doc.type == "Pavers":
				if m.item not in job_work_cost:
					job_work_cost[m.item] = {'amount': 0, 'rate': []}
				job_work_cost[m.item]['amount'] += m.amount or 0
				job_work_cost[m.item]['rate'].append(m.rate or 0)

				if m.is_customer_scope_expense != 'Yes':
					if m.item not in job_work_cost_without_cs:
						job_work_cost_without_cs[m.item] = {'amount': 0, 'rate': []}
					job_work_cost_without_cs[m.item]['amount'] += m.amount or 0
					job_work_cost_without_cs[m.item]['rate'].append(m.rate or 0)

			jw_amt += m.amount or 0
			jw_rate.append(m.rate or 0)

			if m.is_customer_scope_expense != 'Yes':
				jw_amt_without_cs += m.amount or 0
				jw_rate_without_cs.append(m.rate or 0)

	item_cost = []
	for item in doc.delivery_detail:
		if doc.type != "Pavers":
			job_work_cost[item.item] =  {'amount': jw_amt, 'rate': jw_rate}
			job_work_cost_without_cs[item.item] =  {'amount': jw_amt_without_cs, 'rate': jw_rate_without_cs}
		date = item.creation
		bin_ = get_item_price_list_rate(item = item.item, date = date)
		cost=(bin_ or 0)* (((item.delivered_stock_qty or 0) + (item.returned_stock_qty or 0)))
		item_cost.append({
		 "item" : item.item,
		 "qty" : ((item.delivered_stock_qty or 0) + (item.returned_stock_qty or 0)),
		 "uom": frappe.db.get_value("Item", item.item, "stock_uom"),
		 "rate" : bin_,
		 "amount": cost
		})
	
	for i in job_work_cost:
		if (isinstance(job_work_cost[i].get('rate'), list)):
			job_work_cost[i]['rate'] = sum(job_work_cost[i]['rate'])/(len(job_work_cost[i]['rate']) or 1)

	for i in job_work_cost_without_cs:
		if (isinstance(job_work_cost_without_cs[i].get('rate'), list)):
			job_work_cost_without_cs[i]['rate'] = sum(job_work_cost_without_cs[i]['rate'])/(len(job_work_cost_without_cs[i]['rate']) or 1)
	
	unrelated_other_per_sqft = unrelated_other_cost / (unrelated_other_sqft or 1)
	unrelated_other_per_sqft_without_cs = unrelated_other_cost_without_cs / (unrelated_other_sqft_without_cs or 1)

	res = {
		"additional_cost": add_cost,
		"rental": rental_cost,
		"item_cost": item_cost,
		"own_vehicle": doc.transporting_cost or 0,
		"job_work_rate": job_work_cost,
		"other_rate": other_cost,
		"unrelated_other_cost": unrelated_other_cost,
		"unrelated_other_sqft": unrelated_other_sqft,
		"unrelated_other_per_sqft": unrelated_other_per_sqft,

		# Expense without customer scope

		"additional_cost_without_cs": add_cost_without_cs,
		"rental_without_cs": rental_cost_without_cs,
		"own_vehicle_without_cs": (doc.transporting_cost or 0) - (doc.customer_scope_transporting_cost or 0),
		"job_work_rate_without_cs": job_work_cost_without_cs,
		"other_rate_without_cs": other_cost_without_cs,
		"unrelated_other_cost_without_cs": unrelated_other_cost_without_cs,
		"unrelated_other_sqft_without_cs": unrelated_other_sqft_without_cs,
		"unrelated_other_per_sqft_without_cs": unrelated_other_per_sqft_without_cs,
	}

	return res

def get_site_sales_order_item_prices(site):
	return {
		'paver': frappe.db.sql(f"""
							select 
			 					soi.item_code as item,
								soi.rate,
								so.name as sales_order
							from `tabSales Order Item` soi
							inner join `tabSales Order` so
							on so.name = soi.parent
							where 
							   so.docstatus = 1 and
							   so.site_work = '{site}' and
							   soi.item_group = 'Pavers'
							""", as_dict=True),
		'compound_wall': frappe.db.sql(f"""
							select 
				 				soi.item_code as item,
								soi.rate,
								so.name as sales_order
							from `tabSales Order Item` soi
							inner join `tabSales Order` so
							on so.name = soi.parent
							where 
							   so.docstatus = 1 and
							   so.site_work = '{site}' and
							   soi.item_group = 'Compound Walls'
							""", as_dict=True),
	}

def get_site_supply_and_return_trip_details(sitename):
	supply = lambda is_return = 0: frappe.db.sql(f"""
			select 
				sum(ifnull(dni.qty, 0)) as qty,
				dni.uom
			from `tabDelivery Note Item` dni
			inner join `tabDelivery Note` dn
			where dn.name = dni.parent and
				dn.docstatus = 1 and
				dn.site_work = '{sitename}' and
				dni.item_group in ('Pavers', 'Compound Walls') and
				dn.is_return = {is_return}
			group by dni.uom
			""", as_dict=True)
	
	supply_details = supply(0)
	return_details = supply(1)
	return {
		'supply': {
			'no_of_trips': frappe.db.count('Delivery Note', filters={'docstatus': 1, 'is_return': 0, 'site_work': sitename}),
			'qty': ", ".join([f"""{round(i.qty, 2)} {i.uom}""" for i in supply_details]),
			'int_qty': sum([i.qty or 0 for i in supply_details])
		},
		'return': {
			'no_of_trips': frappe.db.count('Delivery Note', filters={'docstatus': 1, 'is_return': 1, 'site_work': sitename}),
			'qty': ", ".join([f"""{round(i.qty, 2)} {i.uom}""" for i in return_details]),
			'int_qty': sum([i.qty or 0 for i in return_details])
		}
	}

def get_item_wise_so_rate(sitename):
	res = {}
	sales_orders = frappe.db.get_all("Sales Order", {"docstatus": 1, "project": sitename})
	for so in sales_orders:
		for row in frappe.get_all("Sales Order Item", {"parenttype": "Sales Order", "parent": so.name}, ["item_code", "rate"]):
			res[row.item_code] = row.rate
	
	return res

def get_item_wise_completion_rate(sitename):
	res = {}
	rates = frappe.db.get_all("Site Completion Rate", {"parent": sitename, "parenttype": 'Project'}, ['item_code', 'rate'], group_by = 'item_code')
	for rate in rates:
		res[rate.item_code] = rate.rate
	
	return res

