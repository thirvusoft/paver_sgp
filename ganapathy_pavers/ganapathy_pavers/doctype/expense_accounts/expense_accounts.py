# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import erpnext
from erpnext.accounts.utils import get_children
from frappe.model.document import Document

class ExpenseAccounts(Document):
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
			if account in [row.paver_account, row.cw_account, row.fp_account, row.lg_account]:
				res["paver"], res["cw"], res["fp"], res["lg"]=[row.paver_account, row.cw_account, row.fp_account, row.lg_account]
				return res
		return res
	
	def get_tree(self,root, company, from_date, to_date):
		for i in root:
			child = self.get_tree(get_children('Account', i.value, company), company, from_date, to_date)
			i['child_nodes']=get_account_balances(child, company, from_date, to_date)
		return root

	def tree_node(self, from_date, to_date, company=erpnext.get_default_company(), parent = "", doctype='Account') -> list:
		root = get_account_balances(get_children(doctype, parent or company, company), company, from_date, to_date)
		return (self.get_tree(root, company, from_date, to_date))
	
@frappe.whitelist()
def get_common_account(account):
	exp=frappe.get_single("Expense Accounts")
	return exp.get_common_account(account)

def get_account_balances(accounts, company, from_date, to_date):
	for account in accounts:
		balance=get_account_balance_on(account, company, from_date, to_date)
		account['balance']=balance or 0
	return accounts

def get_account_balance_on(account, company, from_date, to_date):
	if(account.get('expandable')):
		return 0
	query=f"""
		select sum(debit) as debit from `tabGL Entry` where company='{company}' and
		date(posting_date)>'{from_date}' and date(posting_date)<'{to_date}' and is_cancelled=0
		and account='{account['value']}'
	"""
	balance=frappe.db.sql(query, as_list=True)
	return balance[0][0]