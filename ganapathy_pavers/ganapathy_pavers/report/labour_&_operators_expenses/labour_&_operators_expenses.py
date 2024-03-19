from statistics import mean
import frappe
 
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	machine=filters.get("machine", [])
	pm_filt = "where docstatus!=2 and is_sample=0 "
	sbc_filt= "where docstatus!=2"
	cw_filt = "where docstatus!=2 and IFNULL(type, '')!='' "

	if from_date:
		pm_filt += " and from_time >= '{0}' ".format(from_date)
		sbc_filt += " and from_time >= '{0}' ".format(from_date)
		cw_filt+=  " and molding_date>='{0}' ".format(from_date)
	if to_date:
		pm_filt += " and from_time <= '{0}' ".format(to_date + " 23:59:59")
		sbc_filt += " and from_time <= '{0}' ".format(to_date + " 23:59:59")
		cw_filt+=  " and molding_date <= '{0}' ".format(to_date)
		
	if machine:
		if len(machine) == 1:
			pm_filt += " and work_station = '{0}' ".format(machine[0])
		else:
			pm_filt += " and work_station in {0} ".format(tuple(machine))


	data=[]
	pw_manufacturing=frappe.db.sql("""
	select 
		"Paver" as type,
		SUM(labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense) as total_labour_cost,
		SUM(operators_cost_in_manufacture+operators_cost_in_rack_shift) as total_operator_cost,
		AVG((labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense))/AVG(total_production_sqft) as labour_cost,
		AVG((operators_cost_in_manufacture+operators_cost_in_rack_shift))/AVG(total_production_sqft) as operator_cost,
		SUM(total_production_sqft) as production_sqft
		from `tabMaterial Manufacturing` {0}""".format(pm_filt), as_dict=1)
	
	shot_blast_costing=frappe.db.sql("""
	select 
		"Shot Blast" as type,
		SUM(labour_cost) as total_labour_cost,
		AVG(labour_cost)/AVG(total_sqft) as labour_cost,
		SUM(total_sqft) as production_sqft
		from `tabShot Blast Costing` {0}""".format(sbc_filt), as_dict=1)
	
	cw_manufacturing=frappe.db.sql("""
	select 
		type,
		SUM(total_labour_wages + labour_expense_for_curing) as total_labour_cost,
		SUM(total_operator_wages) as total_operator_cost,
		AVG(total_labour_wages + labour_expense_for_curing)/AVG(production_sqft) as labour_cost,
		AVG(total_operator_wages)/AVG(production_sqft) as operator_cost,
		SUM(production_sqft) as production_sqft
		from `tabCW Manufacturing` {0}
		GROUP BY type
		""".format(cw_filt), as_dict=1)
	
	data += cw_manufacturing
	
	if pw_manufacturing and pw_manufacturing[0]:
		data.append(pw_manufacturing[0])
	
	if shot_blast_costing and shot_blast_costing[0]:
		data.append(shot_blast_costing[0])
		
	columns = get_columns()
	data.sort(key = lambda row: row.get("type", ""))
	return columns, data
	
def get_columns():
   columns = [
	   {
		"fieldname": "type",
		"label": "Manufacturing",
		"fieldtype": "Data"
	   },
	   {
		"fieldname": "total_labour_cost",
		"label": "Total Labour Cost",
		"fieldtype": "Currency"
	   },
	   {
		"fieldname": "labour_cost",
		"label": "Labour Cost Per SQF",
		"fieldtype": "Currency"
	   },
	   {
		"fieldname": "total_operator_cost",
		"label": "Total Operator Cost",
		"fieldtype": "Currency"
	   },
	   {
		"fieldname": "operator_cost",
		"label": "Operator Cost Per SQF",
		"fieldtype": "Currency"
	   },
	   {
		"fieldname": "production_sqft",
		"label": "Production Sqft",
		"fieldtype": "Float"
	   }
	]
  
   return columns
