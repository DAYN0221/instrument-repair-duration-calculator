import requests

url = "http://localhost:12123/generate_maintenance_quote"
data = {
    "cust_name": "中国科学院半导体研究所",
    "cust_add": "",
    "cust_phone": "18801087197",
    "cust_contact": "徐文奇",
    "device_type": "锁相放大器",
    "device_sn": "44175A",
    "device_err": "超量程",
    "dtc_rslt": "仪器开机自检BATT失败，控制板损坏；进入测试界面后SIGNAL INPUT和SENSITIVITY报错OVLD，模拟板损坏；",
    "total_fee": "7006",
    "device_model": "SR830",
    "accessories": "纸箱",
    "repair_plan": "更换控制板组件，更换模拟板组件，检测仪器。",
    "maint_eng_id": "王力争",
}

response = requests.post(url, json=data)
print(response.text)
