import requests

url = "http://localhost:12123/generate_delivery_note"
data = {
    "customerDeliveryAddress": "西安市高新区科技路123号",
    "instmtModel": "DSO-X 3024A",
    "instmtSerialNumber": "SN2023123456",
    "instmtAccessoriesInfo": "电源线, 探头x2, 说明书",
    "salesRpstv": "张三",
}

response = requests.post(url, json=data)
print(response.json())
