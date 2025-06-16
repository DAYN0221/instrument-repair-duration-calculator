import requests

print("测试工作日API...")
try:
    response = requests.get(
        "https://date.appworlds.cn/work/days",
        params={'startDate': '2024-01-01', 'endDate': '2024-01-31'}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"API调用成功: {data}")
    else:
        print(f"HTTP错误: {response.status_code}")
except Exception as e:
    print(f"API调用失败: {e}")