# Copyright (c) 2026, Administrator and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestLibraryTransaction(FrappeTestCase):
	def setUp(self):
		# Clean up any leftover test data
		frappe.db.delete("Library Transaction")
		frappe.db.delete("Library Membership")

		# Ensure a clean test Article exists
		if not frappe.db.exists("Article", "Test Book"):
			self.article = frappe.get_doc({
				"doctype": "Article",
				"article_name": "Test Book",
				"status": "Available"
			}).insert()
		else:
			self.article = frappe.get_doc("Article", "Test Book")
			self.article.status = "Available"
			self.article.save()

		# Ensure a clean test Member exists
		if not frappe.db.exists("Library Member", {"email_address": "testmember@example.com"}):
			self.member = frappe.get_doc({
				"doctype": "Library Member",
				"first_name": "Test",
				"last_name": "Member",
				"email_address": "testmember@example.com"
			}).insert()
		else:
			self.member = frappe.get_doc("Library Member", {"email_address": "testmember@example.com"})

	def test_issue_without_membership_fails(self):
		# Attempting to issue without an active membership must throw an exception
		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": self.article.name,
			"library_member": self.member.name,
			"type": "Issue",
			"date": today()
		})
		self.assertRaises(frappe.ValidationError, txn.submit)

	def test_issue_with_membership_and_duplicate_issue(self):
		# 1. Create a valid membership
		membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": self.member.name,
			"from_date": today(),
			"to_date": add_days(today(), 30),
			"paid": 1
		})
		membership.submit()

		# 2. Issue should succeed
		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": self.article.name,
			"library_member": self.member.name,
			"type": "Issue",
			"date": today()
		})
		txn.submit()
		self.assertEqual(txn.docstatus, 1)

		# 3. Issuing the same article again must fail
		second_txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": self.article.name,
			"library_member": self.member.name,
			"type": "Issue",
			"date": today()
		})
		self.assertRaises(frappe.ValidationError, second_txn.submit)
