from frappe import _

def get_purchase_invoice_dashboard(data):
    return {
        "fieldname": "custom_stone_confirmation_id",
        "transactions": [
            {
                "label": _("Linked With"),
                "items": ["Stone Confirmation"]
            }
        ]
    }
