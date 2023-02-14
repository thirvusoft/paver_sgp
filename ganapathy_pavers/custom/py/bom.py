import frappe

def update_latest_price_in_all_boms():
	if frappe.db.get_single_value("Manufacturing Settings", "update_bom_costs_automatically"):
		update_cost()

def update_cost():
	frappe.db.auto_commit_on_many_writes = 1
	bom_list = get_boms_in_bottom_up_order()
	for bom in bom_list:
		frappe.get_doc("BOM", bom).update_cost(update_parent=False, from_child_bom=True)

	frappe.db.auto_commit_on_many_writes = 0


def get_boms_in_bottom_up_order(bom_no=None):
	def _get_parent(bom_no):
		return frappe.db.sql_list("""
			select distinct bom_item.parent from `tabBOM Item` bom_item
			where bom_item.bom_no = %s and bom_item.docstatus=1 and bom_item.parenttype='BOM'
				and exists(select bom.name from `tabBOM` bom where bom.name=bom_item.parent and bom.is_active=1)
		""", bom_no)

	count = 0
	bom_list = []
	if bom_no:
		bom_list.append(bom_no)
	else:
		# get all leaf BOMs
		bom_list = frappe.db.sql_list("""select name from `tabBOM` bom
			where docstatus!=2 and is_active=1
				and not exists(select bom_no from `tabBOM Item`
					where parent=bom.name and ifnull(bom_no, '')!='')""")

	while(count < len(bom_list)):
		for child_bom in _get_parent(bom_list[count]):
			if child_bom not in bom_list:
				bom_list.append(child_bom)
		count += 1

	return bom_list