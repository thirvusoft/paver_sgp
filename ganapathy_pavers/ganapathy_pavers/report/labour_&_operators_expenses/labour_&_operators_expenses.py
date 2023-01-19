from statistics import mean
import frappe
 
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	machine=filters.get("machine", [])
	pm_filt = "where docstatus!=2"
	cw_filt = "where docstatus!=2 and IFNULL(type, '')!='' "

	if from_date:
		pm_filt += " and from_time >= '{0}' ".format(from_date)
		cw_filt+=  " and molding_date>='{0}' ".format(from_date)
	if to_date:
		pm_filt += " and from_time <= '{0}' ".format(to_date + " 23:59:59")
		cw_filt+=  " and molding_date <= '{0}' ".format(to_date)
		
	if machine:
		if len(machine) == 1:
			pm_filt += " and work_station = '{0}' ".format(machine[0])
		else:
			pm_filt += " and work_station in {0} ".format(tuple(machine[0]))


	data=[]
	pw_manufacturing=frappe.db.sql("""
	select 
		"Paver" as type,
		SUM(labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense) as total_labour_cost,
		SUM(operators_cost_in_manufacture+operators_cost_in_rack_shift) as total_operator_cost,
		AVG((labour_cost_manufacture+labour_cost_in_rack_shift+labour_expense))/AVG(production_sqft) as labour_cost,
		AVG((operators_cost_in_manufacture+operators_cost_in_rack_shift))/AVG(production_sqft) as operator_cost,
		SUM(production_sqft) as production_sqft
		from `tabMaterial Manufacturing` {0}""".format(pm_filt), as_dict=1)
	
	cw_manufacturing=frappe.db.sql("""
	select 
		CASE 
			WHEN type not in ("Post", "Slab") 
			THEN type 
			ELSE "Compound Wall" 
		END as type,
		SUM(total_labour_wages + labour_expense_for_curing) as total_labour_cost,
		SUM(total_operator_wages) as total_operator_cost,
		AVG(total_labour_wages + labour_expense_for_curing)/AVG(production_sqft) as labour_cost,
		AVG(total_operator_wages)/AVG(production_sqft) as operator_cost,
		SUM(production_sqft) as production_sqft
		from `tabCW Manufacturing` {0}
		GROUP BY CASE
            WHEN type not in ('Post', 'Slab') 
			THEN type
        END
		""".format(cw_filt), as_dict=1)
	
	post_slab={}
	for row in cw_manufacturing:
		if row.get("type") in []:
			if not post_slab:
				post_slab=row
				post_slab["type"]="Compound Wall"
			else:
				post_slab["total_labour_cost"] += row.get("total_labour_cost", 0)
				post_slab["labour_cost"] = (post_slab.get("labour_cost", 0)+row.get("labour_cost", 0))/2
				post_slab["total_operator_cost"] += row.get("total_operator_cost", 0)
				post_slab["operator_cost"] = (post_slab.get("operator_cost", 0)+row.get("operator_cost", 0))/2
				post_slab["production_sqft"] = post_slab.get("production_sqft", 0)+row.get("production_sqft", 0)
			continue
		data.append(row)
	
	if post_slab:
		data.append(post_slab)
	
	if pw_manufacturing and pw_manufacturing[0]:
		data.append(pw_manufacturing[0])
		
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
