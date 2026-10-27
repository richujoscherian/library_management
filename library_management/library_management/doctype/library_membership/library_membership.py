# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class LibraryMembership(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		from_date: DF.Date
		full_name: DF.Data | None
		library_member: DF.Link
		paid: DF.Check
		to_date: DF.Date | None
	# end: auto-generated types

	def before_submit(self):
		exists = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": 1,
				# check if the membership's to_date is later than this membership's from_date
				"to_date": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("There is an active membership for this member")

		# get loan period from Library Settings
		loan_period = frappe.db.get_single_value("Library Settings", "loan_period") or 30
		self.to_date = add_days(self.from_date, loan_period)
