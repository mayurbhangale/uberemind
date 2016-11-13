import sendgrid

sg = sendgrid.SendGridAPIClient(apikey='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')
email= 'mayurbhangale96@gmail.com'
send_time = "12:31:18"

data = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": "mayurbhangale96@gmail.com"
                    }
                ],
                "subject": "Time to book Uber!"
            }
        ],
        "send_at": 1409348513,
        "from": {
            "email": email
        },
        "content": [
            {
                "type": "text/plain",
                "value": "Hello, Its time to book your cab!"
            }
        ]
}
response = sg.client.mail.send.post(request_body=data)
print(response.status_code)
print(response.body)
print(response.headers)