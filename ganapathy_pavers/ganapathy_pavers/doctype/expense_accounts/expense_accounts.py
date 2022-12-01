# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExpenseAccounts(Document):
	def get_common_account(self, account):
		res={"paver": "", "cw": "", "fp": "", "lg": ""}
		for row in self.expense_account_common_groups:
			if account in [row.paver_account, row.cw_account, row.fp_account, row.lg_account]:
				res["paver"], res["cw"], res["fp"], res["lg"]=[row.paver_account, row.cw_account, row.fp_account, row.lg_account]
				return res
		return res
	
@frappe.whitelist()
def get_common_account(account):
	exp=frappe.get_single("Expense Accounts")
	return exp.get_common_account(account)