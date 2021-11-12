import requests 
import json 

file = open('/Users/bhavsha2/Documents/terraform_rev/vpc/terraform.tfstate').read()
j= json.loads(file)

url=j['outputs']['public_ip']['value']

url= 'http://' + url


try:
    resp = requests.get(url, timeout=3) #3 seconds
except Exception:
    print ("Note : Challenge Failed, Please try again")


#My External IP validation
url= 'https://emlxxz79gg.execute-api.ap-south-1.amazonaws.com/dev?publicip=35.154.116.55'

extresp = requests.request("GET", url)

if resp.status_code == 200:

    if 'timed' in extresp.text:



        print ("Note:Challenge Validated Successfully --- flag{Cloud_security_Infra_important}")


    else:


        print ("Note Challenge Failed, Please try again")
else:

    print ("Note Challenge Failed, Please try again")






