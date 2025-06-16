# 仪器维修时长计算系统

基于FastAPI构建的仪器维修时长计算和超期判断系统，支持中国法定节假日的工作日计算。

## 功能特性

### 1. 工作日计算
- **智能API集成**: 优先使用 `https://date.appworlds.cn/work/days` API获取精确的工作日数据
- **自动排除节假日**: API自动处理中国法定节假日，无需手动维护节假日列表
- **缓存机制**: 相同日期范围的查询结果会被缓存，提高响应速度
- **降级处理**: API失败时自动降级到本地计算（排除周末）
- **分段查询**: 支持超过一年的日期范围，自动分段处理

### 2. 维修时长计算

#### 普通维修仪器 (rep_ins_type ≠ 3)
- **检测时长**: 提交报价时间 - 派工时间 ≤ 7个工作日
- **维修时长**: 提交质检时间 - 合同审核通过时间 ≤ 10个工作日

#### 返修仪器 (rep_ins_type = 3)
- **返修时长**: 提交质检时间 - 派工时间 ≤ 10个工作日

### 3. 超期判断
- 自动判断各阶段是否超过规定工作日
- 返回详细的超期状态信息

## 项目结构

```
pyDocTemplate/
├── main.py              # 主应用文件
├── demo.py              # 演示脚本
├── test_api.py          # 基础API测试文件
├── test_workday_api.py  # 工作日API集成测试文件
├── quick_test.py        # 快速API测试脚本
├── simple_test.py       # 简单功能测试脚本
├── requirements.txt     # 依赖包列表
├── README.md           # 项目说明文档
├── generated_files/    # 生成的文件目录
├── temp/               # 模板文件目录
└── venv/               # 虚拟环境目录
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:12123` 启动

### 3. 查看API文档

- Swagger UI: http://localhost:12123/docs
- ReDoc: http://localhost:12123/redoc

## API接口

### 1. 计算维修时长 `/calculate_repair_time`

**POST** 请求，用于计算维修各阶段时长并判断是否超期。

#### 请求参数

```json
{
  "rep_ins_type": 1,                    // 仪器类型，3为返修，其他为普通维修
  "rep_start_date": "2024-03-01 09:00:00",  // 派工时间戳
  "quot_start_date": "2024-03-08 17:00:00", // 提交报价时间戳（可选）
  "detec_start_date": "2024-03-10 09:00:00", // 合同审核通过时间戳（可选）
  "qc_start_time": "2024-03-25 16:00:00"    // 提交质检时间戳（可选）
}
```

#### 响应结果

```json
{
  "rep_ins_type": 1,
  "detection_days": 5,           // 检测时长（工作日）
  "repair_days": 11,             // 维修时长（工作日）
  "return_repair_days": null,    // 返修时长（工作日）
  "is_detection_overdue": false, // 检测是否超期
  "is_repair_overdue": true,     // 维修是否超期
  "is_return_repair_overdue": null, // 返修是否超期
  "message": "计算完成"
}
```

### 2. 生成维修确认单 `/generate_maintenance_quote`

**POST** 请求，用于生成维修确认单文档。

### 3. 系统信息 `/`

**GET** 请求，获取系统基本信息和可用接口列表。

## 使用示例

### 1. 运行测试脚本

**基础功能测试**:
```bash
python test_api.py
```

**工作日API集成测试**:
```bash
python test_workday_api.py
```

**快速验证**:
```bash
python quick_test.py
```

### 2. 使用curl测试

```bash
# 测试普通维修仪器
curl -X POST "http://localhost:12123/calculate_repair_time" \
     -H "Content-Type: application/json" \
     -d '{
       "rep_ins_type": 1,
       "rep_start_date": "2024-03-01 09:00:00",
       "quot_start_date": "2024-03-08 17:00:00",
       "detec_start_date": "2024-03-10 09:00:00",
       "qc_start_time": "2024-03-25 16:00:00"
     }'

# 测试返修仪器
curl -X POST "http://localhost:12123/calculate_repair_time" \
     -H "Content-Type: application/json" \
     -d '{
       "rep_ins_type": 3,
       "rep_start_date": "2024-03-01 09:00:00",
       "qc_start_time": "2024-03-20 16:00:00"
     }'
```

### 3. Python代码示例

```python
import requests

# 计算维修时长（使用API集成）
data = {
    "rep_ins_type": 1,
    "rep_start_date": "2024-03-01 09:00:00",
    "quot_start_date": "2024-03-08 17:00:00",
    "detec_start_date": "2024-03-10 09:00:00",
    "qc_start_time": "2024-03-25 16:00:00"
}

response = requests.post("http://localhost:12123/calculate_repair_time", json=data)
result = response.json()

print(f"检测时长: {result['detection_days']} 工作日")
print(f"维修时长: {result['repair_days']} 工作日")
print(f"检测是否超期: {result['is_detection_overdue']}")
print(f"维修是否超期: {result['is_repair_overdue']}")

# 直接测试工作日API
api_response = requests.get(
    "https://date.appworlds.cn/work/days",
    params={'startDate': '2024-03-01', 'endDate': '2024-03-08'}
)
api_data = api_response.json()
print(f"API返回工作日数: {api_data['data']}")
```

## 日期格式支持

系统支持多种日期时间格式：

- ISO格式: `2024-03-01T09:00:00`
- 标准格式: `2024-03-01 09:00:00`
- 日期格式: `2024-03-01`
- 带时区格式: `2024-03-01T09:00:00Z`

## 工作日API集成

### API信息
- **API地址**: `https://date.appworlds.cn/work/days`
- **请求方式**: GET/POST
- **请求限制**: 免费用户1秒1次，日请求量不超过1千次
- **支持范围**: 最大支持查询一年范围

### 功能特性
1. **自动节假日处理**: API自动处理中国法定节假日，无需手动维护
2. **智能缓存**: 系统会缓存API查询结果，避免重复请求
3. **容错机制**: API失败时自动降级到本地计算
4. **分段查询**: 超过一年的日期范围会自动分段处理

### 测试API集成

**完整测试套件**:
```bash
python test_workday_api.py
```

**快速API验证**:
```bash
python quick_test.py
```

**简单功能测试**:
```bash
python simple_test.py
```

这些测试脚本会验证：
- API直接调用功能
- 系统集成效果
- 缓存机制
- 频率限制处理
- 基本功能验证

## 注意事项

1. **工作日计算**: 优先使用API获取精确的工作日数据，包含中国法定节假日
2. **API限制**: 免费用户有频率限制（1秒1次），系统已实现缓存和降级机制
3. **时长计算**: 不包含起始日期，只计算中间的完整工作日
4. **超期判断**: 严格按照工作日计算，不是自然日
5. **容错处理**: API失败时会自动降级到本地计算（仅排除周末）
6. **网络依赖**: 首次查询需要网络连接，后续相同查询使用缓存

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器
- **python-docx**: Word文档处理
- **Requests**: HTTP请求库，用于API调用
- **工作日API**: 中国法定节假日数据源

## 开发和扩展

### 配置API设置

在 `main.py` 中修改API配置：

```python
# 修改API地址（如果需要）
WORKDAY_API_URL = "https://your-custom-api.com/workdays"

# 清空缓存
_workday_cache.clear()
```

### 修改超期标准

在 `calculate_repair_time` 函数中修改对应的天数限制：

```python
result.is_detection_overdue = result.detection_days > 7  # 修改检测超期标准
result.is_repair_overdue = result.repair_days > 10       # 修改维修超期标准
```

## 许可证

本项目采用 MIT 许可证。