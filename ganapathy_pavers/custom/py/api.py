# Whatsapp Integration

#Send Invoice

import http.client
import json
import frappe
from frappe.utils.password import get_decrypted_password
from frappe.utils.csvutils import getlink

@frappe.whitelist()
def send_invoice(cus, name, doctype):

  link=frappe.get_value(doctype, name, 'print_link') or None
  if(link):
    link=frappe.utils.get_url()+link
    mb=frappe.get_doc(doctype, name)
    if not mb.supervisor_phone_no:
      return
    ts_api=frappe.db.get_single_value('Interakt Settings', 'api_endpoint')
    if(not ts_api):
      frappe.throw('Please Enter 	API Endpoint in '+getlink('interakt-settings', ''))
    conn = http.client.HTTPSConnection(ts_api)
    payload = json.dumps({
    "countryCode": "+91",
    "phoneNumber": mb.supervisor_phone_no,
    "callbackData": "some text here",
    "type": "Template",
    "template": {
      "name": "registration_confirmation_op",
      "languageCode": "en",
      "headerValues": [ link ],
      "fileName": frappe.get_value(doctype, name, 'ts_file') or None,
    
      "bodyValues": [
        "Mani"
      ]
    },
  })
    headers = {
    'Authorization': get_decrypted_password('Interakt Settings', 'Interakt Settings', 'api_key'),
    'Content-Type': 'application/json',
    'Cookie': 'ApplicationGatewayAffinity=a8f6ae06c0b3046487ae2c0ab287e175; ApplicationGatewayAffinityCORS=a8f6ae06c0b3046487ae2c0ab287e175'
  }
    conn.request("POST", "/v1/public/message/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return res