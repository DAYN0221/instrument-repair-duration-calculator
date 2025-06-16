#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪器维修时长计算API测试文件

使用示例：
python test_api.py
"""

import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:12124"

def test_repair_time_calculation():
    """测试维修时长计算功能"""
    print("=== 测试维修时长计算功能 ===")
    
    # 测试案例1：普通维修仪器 (rep_ins_type != 3)
    print("\n1. 测试普通维修仪器：")
    test_data_1 = {
        "rep_ins_type": 1,
        "rep_start_date": "2024-03-01 09:00:00",  # 派工时间
        "quot_start_date": "2024-03-08 17:00:00",  # 提交报价时间
        "detec_start_date": "2024-03-10 09:00:00",  # 合同审核通过时间
        "qc_start_time": "2024-03-25 16:00:00"  # 提交质检时间
    }
    
    response = requests.post(f"{BASE_URL}/calculate_repair_time", json=test_data_1)
    if response.status_code == 200:
        result = response.json()
        print(f"检测时长: {result['detection_days']} 工作日 (是否超期: {result['is_detection_overdue']})")
        print(f"维修时长: {result['repair_days']} 工作日 (是否超期: {result['is_repair_overdue']})")
        print(f"消息: {result['message']}")
    else:
        print(f"请求失败: {response.status_code} - {response.text}")
    
    # 测试案例2：返修仪器 (rep_ins_type == 3)
    print("\n2. 测试返修仪器：")
    test_data_2 = {
        "rep_ins_type": 3,
        "rep_start_date": "2024-03-01 09:00:00",  # 派工时间
        "qc_start_time": "2024-03-20 16:00:00"  # 提交质检时间
    }
    
    response = requests.post(f"{BASE_URL}/calculate_repair_time", json=test_data_2)
    if response.status_code == 200:
        result = response.json()
        print(f"返修时长: {result['return_repair_days']} 工作日 (是否超期: {result['is_return_repair_overdue']})")
        print(f"消息: {result['message']}")
    else:
        print(f"请求失败: {response.status_code} - {response.text}")
    
    # 测试案例3：超期案例
    print("\n3. 测试超期案例：")
    test_data_3 = {
        "rep_ins_type": 1,
        "rep_start_date": "2024-03-01 09:00:00",  # 派工时间
        "quot_start_date": "2024-03-15 17:00:00",  # 提交报价时间（超过7个工作日）
        "detec_start_date": "2024-03-16 09:00:00",  # 合同审核通过时间
        "qc_start_time": "2024-04-10 16:00:00"  # 提交质检时间（超过10个工作日）
    }
    
    response = requests.post(f"{BASE_URL}/calculate_repair_time", json=test_data_3)
    if response.status_code == 200:
        result = response.json()
        print(f"检测时长: {result['detection_days']} 工作日 (是否超期: {result['is_detection_overdue']})")
        print(f"维修时长: {result['repair_days']} 工作日 (是否超期: {result['is_repair_overdue']})")
        print(f"消息: {result['message']}")
    else:
        print(f"请求失败: {response.status_code} - {response.text}")

def test_api_info():
    """测试API信息接口"""
    print("\n=== 测试API信息接口 ===")
    
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        result = response.json()
        print(f"系统信息: {result['message']}")
        print("可用接口:")
        for endpoint, description in result['endpoints'].items():
            print(f"  {endpoint}: {description}")
    else:
        print(f"请求失败: {response.status_code} - {response.text}")

def main():
    """主函数"""
    print("仪器维修时长计算系统 - API测试")
    print("请确保服务器已启动 (python main.py)")
    print("服务器地址:", BASE_URL)
    
    try:
        # 测试服务器连接
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("无法连接到服务器，请检查服务器是否已启动")
            return
    except requests.exceptions.RequestException as e:
        print(f"无法连接到服务器: {e}")
        print("请先启动服务器: python main.py")
        return
    
    # 运行测试
    test_api_info()
    test_repair_time_calculation()
    
    print("\n=== 测试完成 ===")
    print("\n你可以访问以下URL查看API文档:")
    print(f"{BASE_URL}/docs - Swagger UI")
    print(f"{BASE_URL}/redoc - ReDoc")

if __name__ == "__main__":
    main()