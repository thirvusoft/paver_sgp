# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import erpnext
from erpnext.accounts.utils import get_children
from frappe.model.document import Document

class ExpenseAccounts(Document):
	def validate(doc):
		frappe.db.sql("""delete from `tabExpense Account Common Groups` where parenttype='Vehicle' """)
		vehicle_accounts={}
		for row in doc.expense_account_common_groups:
			if row.vehicle:
				if row.vehicle not in vehicle_accounts:
					vehicle_accounts[row.vehicle]=[]
				vehicle_accounts[row.vehicle].append({
					"paver_account":row.paver_account,
					"cw_account":row.cw_account,
					"lg_account":row.lg_account,
					"fp_account":row.fp_account,
					"monthly_cost":row.monthly_cost,
					"vehicle":row.vehicle
				})
		for row in vehicle_accounts:
			vehicle_doc=frappe.get_doc("Vehicle", row)
			vehicle_doc.update({
				"vehicle_common_groups": vehicle_accounts[row]
			})
			vehicle_doc.run_method=lambda *args, **kwargs: 0
			vehicle_doc.save()

	def get_common_account(self, account):
		res={"paver": "", "cw": "", "fp": "", "lg": ""}
		parent_acc=frappe.get_value("Account", account, "parent_account")
		if self.paver_group==parent_acc:
			res['paver']=account
		elif self.cw_group==parent_acc:
			res['cw']=account
		elif self.lg_group==parent_acc:
			res['lg']=account
		elif self.fp_group==parent_acc:
			res['fp']=account
		for row in self.expense_account_common_groups:
			if account in [row.paver_account, row.cw_account, row.fp_account, row.lg_account,row.monthly_cost]:
				res["paver"], res["cw"], res["fp"], res["lg"]=[row.paver_account, row.cw_account, row.fp_account, row.lg_account]
				return res
		return res
	
	def get_tree(self,root, company, from_date, to_date, vehicle=None):
		for i in root:
			child = self.get_tree(get_children('Account', i.value, company), company, from_date, to_date, vehicle)
			i['child_nodes']=get_account_balances(child, company, from_date, to_date, vehicle)
		return root

	def tree_node(self, from_date, to_date, company=erpnext.get_default_company(), parent = "", doctype='Account', vehicle=None) -> list:
		root = get_account_balances(get_children(doctype, parent or company, company), company, from_date, to_date, vehicle)
		return (self.get_tree(root, company, from_date, to_date, vehicle))


def get_tree(root, company):
	for i in root:
		i['child_nodes'] = get_tree(get_children('Account', i.value, company), company)
	return root

def tree_node(company=erpnext.get_default_company(), parent = "", doctype='Account') -> list:
	root = get_children(doctype, parent or company, company)
	return (get_tree(root, company))

@frappe.whitelist()
def get_filter(company=""):
	if not company:
		company=erpnext.get_default_company()
	exp=frappe.get_single("Expense Accounts")
	accounts={'paver': exp.paver_group, 'cw': exp.cw_group, 'fp': exp.fp_group, 'lg': exp.lg_group}
	res={}
	for account in accounts:
		if accounts[account]:
			tree=tree_node(company, accounts[account])
			acc_list=[]
			ret_acc_list=get_filter_list(tree, acc_list)
			res[account]=ret_acc_list
	return res

def get_filter_list(accounts, acc_list):
	for acc in accounts:
		
		if acc.get('expandable')==1:
			acc_list=get_filter_list(acc.get('child_nodes'), acc_list)
		else:
			acc_list.append(acc.get('value'))
	return acc_list

@frappe.whitelist()
def get_common_account(account):
	exp=frappe.get_single("Expense Accounts")
	return exp.get_common_account(account)

def get_account_balances(accounts, company, from_date, to_date, vehicle=None):
	for account in accounts:
		balance, gl_vehicle=get_account_balance_on(account, company, from_date, to_date, vehicle)
		account['balance']=balance or 0
		account['vehicle']=gl_vehicle
	return accounts

def get_account_balance_on(account, company, from_date, to_date, vehicle=None):
	if(account.get('expandable')):
		return 0, ""
	conditions=""
	if vehicle:
		conditions+=f" and IFNULL(vehicle, '')!='' and vehicle='{vehicle}'"
	
	query=f"""
		select sum(debit) as debit, vehicle from `tabGL Entry` where company='{company}' and
		date(posting_date)>='{from_date}' and date(posting_date)<='{to_date}' and is_cancelled=0
		and account='{account['value']}'
	"""+conditions
	balance=frappe.db.sql(query, as_list=True)
	return balance[0][0], balance[0][1] or ""

@frappe.whitelist()
def monthly_cost():
	cost=frappe.get_single("Expense Accounts")
	res1=[]
	for i in cost.expense_account_common_groups:
		res={}
		res["paver"]=i.paver_account 
		res["cw"]=i.cw_account
		res["fp"]=i.fp_account
		res["vehicle"]=i.vehicle
		res["lg"]=i.lg_account
		res["monthly_cost"]=i.monthly_cost
		res1.append(res)
		
	return res1	
		
		
	
