from statistics import mean
import frappe
 
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	machine=filters.get("machine")
	print(machine)
	pm_filt = "where docstatus!=2 and"
	cw_filt = "where docstatus!=2 and"
	sum_labour_cost=0
	sum_operator_cost=0
	if(filters.get('from_date') and (not filters.get('to_date'))):
		pm_filt += " from_time >= '{0}' ".format(from_date)
		cw_filt+=  " molding_date '>=' '{0}' ".format(from_date)
	elif(filters.get('to_date') and (not filters.get('from_date'))):
		pm_filt += " from_time >= '{0}' ".format(to_date)
		cw_filt+=  " molding_date >= '{0}' ".format(to_date)
		
	elif(filters.get('from_date') and filters.get('to_date')):
		pm_filt += " from_time between '{0}' and '{1}' ".format(from_date,to_date)
		cw_filt+=  " molding_date between '{0}' and '{1}' ".format(from_date,to_date)
	
	if filters.get("machine"):
		if len(machine) == 1:
			pm_filt += " and work_station = '{0}' ".format(machine[0])
		else:
			pm_filt += " and work_station in {0} ".format(tuple(machine[0]))


	final_list=[]
	pw_manufacturing=frappe.db.sql("""select "Paver" as type,sum(labour_cost_manufacture) + sum(labour_cost_in_rack_shift) + sum(labour_expense) as total_labour_cost ,sum(operators_cost_in_rack_shift) + sum(operators_cost_in_manufacture) as total_operator_cost,((sum(labour_cost_manufacture) + sum(labour_cost_in_rack_shift) + sum(labour_expense))/production_Sqft) as avg_sqf,count(name) as avg_count,(sum(operators_cost_in_rack_shift) + sum(operators_cost_in_manufacture)/production_sqft) as operator_avg_cost from `tabMaterial Manufacturing` {0}""".format(pm_filt),as_dict=1)
  
	cw_manufacturing=frappe.db.sql("""select type as type,sum(total_labour_wages) + sum(labour_expense_for_curing) as total_labour_cost ,sum(total_operator_wages) as total_operator_cost,sum(labour_cost_per_sqft) as labour_cost_per_sqft,sum(operator_cost_per_sqft) as operator_cost_per_sqft,count(name) as avg_count from `tabCW Manufacturing` {0} group by type""".format(cw_filt),as_dict=1)
	for j in cw_manufacturing:
		if j['type'] == 'Post' or j['type'] == 'Slab':
			sum_labour_cost+=round(j['total_labour_cost'],2)
			sum_operator_cost+=round(j['total_operator_cost'],2)
		else:
			final_list.append([j['type'],round(j['total_labour_cost'],2),round(j['labour_cost_per_sqft']/j['avg_count'],2),round(j['total_operator_cost'],2),round(j['operator_cost_per_sqft']/j['avg_count'],2)])
		final_list.append(["Compound Wall",sum_labour_cost,round(j['labour_cost_per_sqft']/j['avg_count'],2),sum_operator_cost,round(j['operator_cost_per_sqft']/j['avg_count'],2)])
	
	for i in pw_manufacturing:
		if i['total_labour_cost']:
			final_list.append([i['type'],round(i['total_labour_cost'],2),round(i['avg_sqf']/i['avg_count'],2),round(i['total_operator_cost'],2),round(i['operator_avg_cost']/i['avg_count'],2)])
		
	columns = get_columns()
	return columns,final_list
	
def get_columns():
   columns = [
	   ("Manufacturing") + ":Dta:250",
	   ("Total Labour Cost ") + ":Data:250",
	   ("Labour Cost Per SQF ") + ":Data:250",
	   ("Total Operators Cost") + ":Data:250",
	   ("Operator Cost Per SQF ") + ":Data:250",
	  
	  
	   ]
  
   return columns
