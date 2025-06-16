from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import requests

app = FastAPI(title="仪器维修时长计算系统", description="计算仪器维修各阶段时长并判断是否超期")

class RepairTimeCalculationRequest(BaseModel):
    rep_ins_type: int  # 仪器类型，3为返修，其他为普通维修
    rep_start_date: str  # 派工时间戳 (ISO格式)
    quot_start_date: Optional[str] = None  # 提交报价时间戳 (ISO格式)
    detec_start_date: Optional[str] = None  # 合同审核通过时间戳 (ISO格式)
    qc_start_time: Optional[str] = None  # 提交质检时间戳 (ISO格式)

class RepairTimeResult(BaseModel):
    rep_ins_type: int
    detection_days: Optional[int] = None  # 检测时长（工作日）
    repair_days: Optional[int] = None  # 维修时长（工作日）
    return_repair_days: Optional[int] = None  # 返修时长（工作日）
    is_detection_overdue: Optional[bool] = None  # 检测是否超期
    is_repair_overdue: Optional[bool] = None  # 维修是否超期
    is_return_repair_overdue: Optional[bool] = None  # 返修是否超期
    message: str

# 工作日API配置
WORKDAY_API_URL = "https://date.appworlds.cn/work/days"

# 缓存工作日数据，避免重复API调用
_workday_cache = {}

def get_workdays_from_api(start_date: datetime, end_date: datetime) -> int:
    """通过API获取两个日期之间的工作日数量"""
    try:
        # 格式化日期为API要求的格式
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # 检查缓存
        cache_key = f"{start_str}_{end_str}"
        if cache_key in _workday_cache:
            return _workday_cache[cache_key]
        
        # 调用API
        params = {
            'startDate': start_str,
            'endDate': end_str
        }
        
        response = requests.get(WORKDAY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 200:
            workdays = data.get('data', 0)
            # 缓存结果
            _workday_cache[cache_key] = workdays
            return workdays
        else:
            raise Exception(f"API返回错误: {data.get('msg', '未知错误')}")
            
    except Exception as e:
        # API调用失败时，使用本地计算作为备用方案
        print(f"API调用失败，使用本地计算: {str(e)}")
        return calculate_workdays_local(start_date, end_date)

def calculate_workdays_local(start_date: datetime, end_date: datetime) -> int:
    """本地计算工作日数量（备用方案，仅排除周末）"""
    if start_date >= end_date:
        return 0
    
    workdays = 0
    current_date = start_date
    
    while current_date < end_date:
        # 仅排除周末，不考虑节假日
        if current_date.weekday() < 5:  # 0-4为周一到周五
            workdays += 1
        current_date += timedelta(days=1)
    
    return workdays

def calculate_workdays(start_date: datetime, end_date: datetime) -> int:
    """计算两个日期之间的工作日数量（优先使用API）"""
    if start_date >= end_date:
        return 0
    
    # 检查日期范围是否超过一年（API限制）
    if (end_date - start_date).days > 365:
        # 如果超过一年，分段计算
        total_workdays = 0
        current_start = start_date
        
        while current_start < end_date:
            # 计算一年的结束日期
            year_end = datetime(current_start.year + 1, 1, 1)
            current_end = min(year_end, end_date)
            
            # 计算这一段的工作日
            segment_workdays = get_workdays_from_api(current_start, current_end)
            total_workdays += segment_workdays
            
            current_start = current_end
        
        return total_workdays
    else:
        return get_workdays_from_api(start_date, end_date)

def parse_datetime(date_str: str) -> datetime:
    """解析ISO格式的日期时间字符串"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(date_str, '%Y-%m-%d')

@app.post("/calculate_repair_time", response_model=RepairTimeResult)
async def calculate_repair_time(request: RepairTimeCalculationRequest):
    """计算维修时长并判断是否超期"""
    try:
        result = RepairTimeResult(
            rep_ins_type=request.rep_ins_type,
            message="计算完成"
        )
        
        # 解析派工时间
        rep_start = parse_datetime(request.rep_start_date)
        
        if request.rep_ins_type != 3:
            # 一、保修为其他类型的仪器(rep_ins_type不等于3)
            
            # 1. 检测时长≤7个工作日
            # 提交报价时间戳(quot_start_date) - 派工时间戳(rep_start_date)
            if request.quot_start_date:
                quot_start = parse_datetime(request.quot_start_date)
                result.detection_days = calculate_workdays(rep_start, quot_start)
                result.is_detection_overdue = result.detection_days > 7
            
            # 2. 维修时长≤10个工作日
            # 提交质检时间戳(qc_start_time) - 合同审核通过时间戳(detec_start_date)
            if request.qc_start_time and request.detec_start_date:
                qc_start = parse_datetime(request.qc_start_time)
                detec_start = parse_datetime(request.detec_start_date)
                result.repair_days = calculate_workdays(detec_start, qc_start)
                result.is_repair_overdue = result.repair_days > 10
        
        else:
            # 二、保修为返修的仪器(rep_ins_type等于3)
            
            # 3. 返修时长≤10个工作日
            # 提交质检时间戳(qc_start_time) - 派工时间戳(rep_start_date)
            if request.qc_start_time:
                qc_start = parse_datetime(request.qc_start_time)
                result.return_repair_days = calculate_workdays(rep_start, qc_start)
                result.is_return_repair_overdue = result.return_repair_days > 10
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"计算失败: {str(e)}")

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "仪器维修时长计算系统",
        "endpoints": {
            "/calculate_repair_time": "计算维修时长并判断是否超期",
            "/docs": "API文档"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=12124)