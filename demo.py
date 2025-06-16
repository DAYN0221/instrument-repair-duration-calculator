import requests

url = "http://localhost:12124/generate_maintenance_quote"
data = {
    "cust_name": "西安电子科技大学",
    "cust_add": "陕西省西安市雁塔区太白南路2号",
    "cust_phone": "029-88201234",
    "cust_contact": "张老师",
    "device_type": "示波器",
    "device_sn": "DSO-X 3024A-123456",
    "device_err": "开机无显示，通道2无信号",
    "dtc_rslt": "电源模块损坏，需更换电容",
    "total_fee": 1500.00,
    "device_model": "Keysight DSO-X 3024A",
    "accessories": "电源线×1，探头×2",
    "repair_plan": "更换电源模块并校准",
    "maint_eng_id": "达工"
}

response = requests.post(url, json=data)
print(response.json())