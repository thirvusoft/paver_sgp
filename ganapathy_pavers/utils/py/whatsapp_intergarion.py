@frappe.whitelist()

def send_invoice(mobile_no, link,filename, cus_name, event):
	
	if(map_link):
		body_value.append(map_link)
	temp_name= "registration_confirmation_op" if(len(body_value)==2) else  "registration_confirmation"
	if(link):
		link=frappe.utils.get_url()+link
		conn = http.client.HTTPSConnection("api.interakt.ai")
		payload = json.dumps({
		"countryCode": "+91",
		"phoneNumber": 7010072040,
		"callbackData": "some text here",
		"type": "Template",
		"template": {
		"name": temp_name,
		"languageCode": "en",
		"headerValues": [ link ],
		"fileName": filename,
		"bodyValues": body_value
		}
	})
		headers = {
		'Authorization': "Basic eHd0aHJaNUp6NjFvZF9qTFYwaml2YV9uSGdIbVR5ZFpad1JtYkREeng5czo=",
		'Content-Type': 'application/json',
		
	}
		conn.request("POST", "/v1/public/message/", payload, headers)
		res = conn.getresponse()
		data = res.read()