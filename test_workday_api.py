#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作日API集成测试文件

测试与 https://date.appworlds.cn/work/days API 的集成
"""

import requests
import json
from datetime import datetime, timedelta

def test_workday_api_direct():
    """直接测试工作日API"""
    print("=== 直接测试工作日API ===")
    
    api_url = "https://date.appworlds.cn/work/days"
    
    # 测试案例1：2024年全年工作日
    print("\n1. 测试2024年全年工作日：")
    params = {
        'startDate': '2025-01-01',
        'endDate': '2025-12-31'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 200:
            print(f"2024年工作日总数: {data.get('data')} 天")
        else:
            print(f"API返回错误: {data.get('msg')}")
    except Exception as e:
        print(f"API调用失败: {str(e)}")
    
    # 测试案例2：2024年3月工作日
    print("\n2. 测试2024年3月工作日：")
    params = {
        'startDate': '2024-03-01',
        'endDate': '2024-03-31'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 200:
            print(f"2024年3月工作日总数: {data.get('data')} 天")
        else:
            print(f"API返回错误: {data.get('msg')}")
    except Exception as e:
        print(f"API调用失败: {str(e)}")
    
    # 测试案例3：包含春节的时间段
    print("\n3. 测试包含春节的时间段（2024年2月）：")
    params = {
        'startDate': '2024-02-01',
        'endDate': '2024-02-29'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 200:
            print(f"2024年2月工作日总数: {data.get('data')} 天")
        else:
            print(f"API返回错误: {data.get('msg')}")
    except Exception as e:
        print(f"API调用失败: {str(e)}")

def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    
    base_url = "http://localhost:12124"
    
    # 测试案例：使用新的API集成计算维修时长
    print("\n测试维修时长计算（使用API集成）：")
    test_data = {
        "rep_ins_type": 1,
        "rep_start_date": "2025-03-01 09:00:00",  # 派工时间
        "quot_start_date": "2025-03-08 17:00:00",  # 提交报价时间
        "detec_start_date": "2025-03-10 09:00:00",  # 合同审核通过时间
        "qc_start_time": "2025-03-25 16:00:00"  # 提交质检时间
    }
    
    try:
        response = requests.post(f"{base_url}/calculate_repair_time", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"检测时长: {result['detection_days']} 工作日 (是否超期: {result['is_detection_overdue']})")
            print(f"维修时长: {result['repair_days']} 工作日 (是否超期: {result['is_repair_overdue']})")
            print(f"消息: {result['message']}")
        else:
            print(f"请求失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"系统集成测试失败: {str(e)}")
        print("请确保服务器已启动: python main.py")

def test_api_rate_limit():
    """测试API频率限制"""
    print("\n=== 测试API频率限制 ===")
    
    api_url = "https://date.appworlds.cn/work/days"
    
    print("连续发送多个请求测试频率限制...")
    
    for i in range(3):
        params = {
            'startDate': '2024-01-01',
            'endDate': '2024-01-31'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == 200:
                print(f"请求 {i+1}: 成功 - 工作日数: {data.get('data')}")
            else:
                print(f"请求 {i+1}: 失败 - {data.get('msg')}")
        except Exception as e:
            print(f"请求 {i+1}: 异常 - {str(e)}")
        
        # 等待1秒以避免频率限制
        if i < 2:
            import time
            time.sleep(1.1)

def test_cache_functionality():
    """测试缓存功能"""
    print("\n=== 测试缓存功能 ===")
    
    base_url = "http://localhost:12124"
    
    # 发送相同的请求两次，第二次应该使用缓存
    test_data = {
        "rep_ins_type": 1,
        "rep_start_date": "2024-01-01 09:00:00",
        "quot_start_date": "2024-01-10 17:00:00"
    }
    
    print("第一次请求（应该调用API）：")
    try:
        start_time = datetime.now()
        response1 = requests.post(f"{base_url}/calculate_repair_time", json=test_data, timeout=10)
        end_time = datetime.now()
        duration1 = (end_time - start_time).total_seconds()
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"检测时长: {result1['detection_days']} 工作日, 耗时: {duration1:.2f}秒")
        else:
            print(f"请求失败: {response1.status_code}")
    except Exception as e:
        print(f"第一次请求失败: {str(e)}")
    
    print("\n第二次请求（应该使用缓存）：")
    try:
        start_time = datetime.now()
        response2 = requests.post(f"{base_url}/calculate_repair_time", json=test_data, timeout=10)
        end_time = datetime.now()
        duration2 = (end_time - start_time).total_seconds()
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"检测时长: {result2['detection_days']} 工作日, 耗时: {duration2:.2f}秒")
            
            if duration2 < duration1:
                print("✓ 缓存生效，第二次请求更快")
            else:
                print("? 缓存可能未生效或网络波动")
        else:
            print(f"请求失败: {response2.status_code}")
    except Exception as e:
        print(f"第二次请求失败: {str(e)}")

def main():
    """主函数"""
    print("工作日API集成测试")
    print("==================")
    
    # 测试API连接
    test_workday_api_direct()
    
    # 测试频率限制
    test_api_rate_limit()
    
    # 测试系统集成
    test_system_integration()
    
    # 测试缓存功能
    test_cache_functionality()
    
    print("\n=== 测试完成 ===")
    print("\n注意事项：")
    print("1. API有频率限制：免费用户1秒1次，日请求量不超过1千次")
    print("2. 系统已实现缓存机制，相同日期范围的查询会使用缓存")
    print("3. API失败时会自动降级到本地计算（仅排除周末）")
    print("4. 支持超过一年的日期范围，会自动分段查询")

if __name__ == "__main__":
    main()