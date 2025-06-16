#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API集成测试
"""

import requests
import time

def test_workday_api():
    """测试工作日API直接调用"""
    print("=== 测试工作日API直接调用 ===")
    
    try:
        # 测试API调用
        response = requests.get(
            "https://date.appworlds.cn/work/days",
            params={'startDate': '2024-01-01', 'endDate': '2024-01-31'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print(f"✅ API调用成功: 2024年1月工作日数 = {data['data']} 天")
            else:
                print(f"⚠️ API返回错误: {data.get('msg', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")

def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    
    try:
        # 测试维修时长计算接口
        data = {
            "rep_ins_type": 1,
            "rep_start_date": "2024-01-01 09:00:00",
            "quot_start_date": "2024-01-05 17:00:00",
            "detec_start_date": "2024-01-08 09:00:00",
            "qc_start_time": "2024-01-15 16:00:00"
        }
        
        response = requests.post(
            "http://localhost:12123/calculate_repair_time",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 系统集成测试成功:")
            print(f"   检测时长: {result['detection_days']} 工作日")
            print(f"   维修时长: {result['repair_days']} 工作日")
            print(f"   检测超期: {result['is_detection_overdue']}")
            print(f"   维修超期: {result['is_repair_overdue']}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        print("   请确保服务器已启动: python main.py")

if __name__ == "__main__":
    print("工作日API集成功能测试")
    print("=" * 30)
    
    # 测试API直接调用
    test_workday_api()
    
    # 等待1秒避免频率限制
    time.sleep(1)
    
    # 测试系统集成
    test_system_integration()
    
    print("\n=== 测试完成 ===")
    print("\n注意事项:")
    print("1. API有频率限制：免费用户1秒1次")
    print("2. 系统已实现缓存机制和降级处理")
    print("3. 支持超过一年的日期范围自动分段查询")