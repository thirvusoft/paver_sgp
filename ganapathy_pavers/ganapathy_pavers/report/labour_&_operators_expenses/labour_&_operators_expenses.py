from statistics import mean
import frappe
 
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	machine=filters.get("machine")
	pm_filt = "where docstatus!=2"
	cw_filt = "where docstatus!=2"
	sum_labour_cost=0
	production_sqft=0
	sum_operator_cost=0
	if(from_date):
		pm_filt += " and from_time >= '{0}' ".format(from_date)
		cw_filt+=  " and molding_date>='{0}' ".format(from_date)
	if(to_date):
		pm_filt += " and from_time <= '{0}' ".format(to_date + " 23:59:59")
		cw_filt+=  " and molding_date <= '{0}' ".format(to_date)
		
	# elif(filters.get('from_date') and filters.get('to_date')):
	# 	pm_filt += " and from_time between '{0}' and '{1}' ".format(from_date,to_date)
	# 	cw_filt+=  " and molding_date between '{0}' and '{1}' ".format(from_date,to_date)
	
	if machine:
		if len(machine) == 1:
			pm_filt += " and work_station = '{0}' ".format(machine[0])
		else:
			pm_filt += " and work_station in {0} ".format(tuple(machine[0]))


	final_list=[]
	pw_manufacturing=frappe.db.sql("""
	select 
		"Paver" as type,
		SUM(labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense) as total_labour_cost,
		SUM(operators_cost_in_manufacture+operators_cost_in_rack_shift) as total_operator_cost,
		AVG((labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense))/AVG(production_sqft) as labour_cost,
		AVG((operators_cost_in_manufacture+operators_cost_in_rack_shift))/AVG(production_sqft) as operator_cost,
		SUM(production_sqft) as production_sqft
		from `tabMaterial Manufacturing` {0}""".format(pm_filt),as_dict=1)
	cw_manufacturing=frappe.db.sql("""
	select 
		type,
		sum(total_labour_wages) + sum(labour_expense_for_curing) as total_labour_cost,
		sum(total_operator_wages) as total_operator_cost,
		sum(labour_cost_per_sqft) as labour_cost_per_sqft,
		sum(operator_cost_per_sqft) as operator_cost_per_sqft,
		SUM(production_sqft) as production_sqft,
		count(name) as avg_count 
		from `tabCW Manufacturing` {0} group by type""".format(cw_filt),as_dict=1)
	for j in cw_manufacturing:
		if j['type'] == 'Post' or j['type'] == 'Slab':
			production_sqft+=j['production_sqft']
			sum_labour_cost+=j['total_labour_cost']
			sum_operator_cost+=j['total_operator_cost']
		else:
			final_list.append([j['type'],j['total_labour_cost'],j['labour_cost_per_sqft']/j['avg_count'],j['total_operator_cost'],j['operator_cost_per_sqft']/j['avg_count'], j["production_sqft"]])
		final_list.append(["Compound Wall",sum_labour_cost,j['labour_cost_per_sqft']/j['avg_count'],sum_operator_cost,j['operator_cost_per_sqft']/j['avg_count'], production_sqft])
	for i in pw_manufacturing:
		if i['total_labour_cost']:
			final_list.append([i['type'],i['total_labour_cost'],i['labour_cost'],i['total_operator_cost'],i['operator_cost'], i['production_sqft']])
		
	columns = get_columns()
	return columns,final_list
	
def get_columns():
   columns = [
	   ("Manufacturing") + ":Dta:250",
	   ("Total Labour Cost ") + ":Data:250",
	   ("Labour Cost Per SQF ") + ":Data:250",
	   ("Total Operators Cost") + ":Data:250",
	   ("Operator Cost Per SQF ") + ":Data:250",
	   {
		"fieldname": "production_sqft",
		"label": "Production Sqft",
		"fieldtype": "Float"
	   }
	   ]
  
   return columns
