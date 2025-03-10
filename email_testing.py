from __future__ import print_function
import time
import brevo_python
from brevo_python.rest import ApiException
from pprint import pprint
import dotenv


brevo_api_key = dotenv.dotenv_values()["BREVO_API_KEY"]
print(brevo_api_key)

# Configure API key authorization: api-key
configuration = brevo_python.Configuration()    
configuration.api_key['api-key'] = brevo_api_key
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api-key'] = 'Bearer'
# Configure API key authorization: partner-key
# configuration = brevo_python.Configuration()
configuration.api_key['partner-key'] = brevo_api_key
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['partner-key'] = 'Bearer'

# create an instance of the API class
api_client = brevo_python.ApiClient(configuration)
api_instance = brevo_python.AccountApi(api_client)

try:
    # Get your account information, plan and credits details
    api_response = api_instance.get_account()
    pprint(api_response)
except ApiException as e:
    print(f"Exception when calling AccountApi->get_account: {e}")

transactional_instance = brevo_python.TransactionalEmailsApi(api_client)
subject = "Thanks for Visiting the Super Fab Lab"
html_content = "<html><body><h1> Thanks for visiting the SFL Today! </h1> <p> We hope you had an amazing time! Please click <a href='https://uncc.instructure.com/enroll/E6NPBA'>this link</a> to join our canvas page and do trainings </p</body></html>"
sender = {"name":"Super Fab Lab","email":"super-fab-lab@c4glenn.com"}
to = [{"email":"psmit145@charlotte.edu","name":"Tano Edwards"}]
send_smtp_email = brevo_python.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)


try:
    start = time.time()
    api_response = transactional_instance.send_transac_email(send_smtp_email)
    end = time.time()
    print(f"Execution took {end - start} seconds")
    pprint(api_response)
except ApiException as e:
    print(f"Exception when calling AccountApi->send_email: {e}")
