# 行政区划代码配置说明

## 概述

行政区划代码现在通过配置文件 `adcode_config.json` 进行管理，支持动态更新，不再硬编码在代码中。

## 配置文件结构

```json
{
  "version": "2025-12-09",
  "source": "https://geo.datav.aliyun.com/areas_v3/bound/100000.json",
  "last_updated": "2025-12-09 14:39:15",
  "adcodes": {
    "中国": "100000",
    "安徽省": "340000",
    "北京市": "110000",
    ...
  }
}
```

## 更新配置

### 自动更新（推荐）

运行更新脚本从 API 获取最新数据：

```bash
python update_adcode_config.py
```

脚本会：

1. 从阿里云 DataV API 获取最新的省级行政区划数据
2. 自动提取所有省级行政区（34 个省级行政区 + 中国）
3. 更新配置文件 `adcode_config.json`
4. 显示新增和移除的行政区

### 手动更新

直接编辑 `adcode_config.json` 文件，添加或修改行政区划代码。

## 使用方法

### 1. 基础使用

```python
from app.services.geo_video.geo_data_manager import GeoDataManager

# 初始化（自动加载配置文件）
manager = GeoDataManager()

# 获取行政区划代码
adcode = manager.get_adcode("安徽省")
print(adcode)  # 输出: 340000
```

### 2. 获取所有省份

```python
# 获取所有可用的省份列表
provinces = manager.get_available_provinces()
print(f"共有 {len(provinces)} 个省级行政区")

for province in provinces:
    adcode = manager.get_adcode(province)
    print(f"{province} - {adcode}")
```

### 3. 查看配置信息

```python
# 获取配置文件信息
config_info = manager.get_config_info()
print(f"配置版本: {config_info['version']}")
print(f"更新时间: {config_info['last_updated']}")
print(f"行政区数量: {config_info['count']}")
```

### 4. 重新加载配置

```python
# 如果配置文件被更新，可以重新加载
success = manager.reload_adcodes()
if success:
    print("配置已重新加载")
```

## 配置文件位置

```
app/services/geo_video/adcode_config.json
```

## 数据源

- **API**: 阿里云 DataV GeoAtlas
- **URL**: https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json
- **说明**: 提供中国省级行政区划的 GeoJSON 数据

## 行政区划代码规则

- **国家级**: 100000（中国）
- **省级**: XXXXXX（6 位数字，后 4 位为 0）
  - 北京市: 110000
  - 天津市: 120000
  - 河北省: 130000
  - ...

## 更新频率建议

- **定期更新**: 每年更新一次（行政区划调整较少）
- **按需更新**: 当发现行政区划有变化时手动更新
- **自动化**: 可以设置定时任务自动运行更新脚本

## 备用方案

如果 API 无法访问，更新脚本会自动使用预定义的行政区划代码（包含 34 个省级行政区）。

## 测试

运行测试脚本验证配置：

```bash
python test_geo_data_manager.py
```

测试内容：

- ✅ 加载配置文件
- ✅ 获取所有省份
- ✅ 获取行政区划代码
- ✅ 下载 GeoJSON 数据
- ✅ 重新加载配置

## 常见问题

### Q1: 配置文件不存在怎么办？

**A**: 运行 `python update_adcode_config.py` 生成配置文件。

### Q2: 如何添加新的行政区？

**A**:

1. 方法 1: 运行更新脚本自动获取最新数据
2. 方法 2: 手动编辑 `adcode_config.json`，添加新的行政区和代码

### Q3: 配置更新后需要重启程序吗？

**A**: 不需要，调用 `manager.reload_adcodes()` 即可重新加载配置。

### Q4: 如何查看当前使用的配置版本？

**A**: 使用 `manager.get_config_info()` 查看配置信息。

## 优势

相比硬编码方式，配置文件方式有以下优势：

1. ✅ **易于维护**: 不需要修改代码，只需更新配置文件
2. ✅ **动态更新**: 支持运行时重新加载配置
3. ✅ **版本管理**: 配置文件包含版本和更新时间信息
4. ✅ **自动化**: 可以通过脚本自动从 API 获取最新数据
5. ✅ **可追溯**: 记录数据源和更新历史
6. ✅ **备用方案**: API 失败时自动使用预定义数据

## 示例输出

### 更新配置

```
============================================================
🗺️  更新行政区划代码配置
============================================================

📥 正在获取中国省级行政区划数据...
尝试获取: https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json
找到 35 个地理要素
  ✓ 北京市                  - 110000 (province)
  ✓ 天津市                  - 120000 (province)
  ...

✓ 成功获取 35 个行政区划代码

============================================================
✓ 配置文件已更新: app\services\geo_video\adcode_config.json
============================================================

✅ 更新完成

配置版本: 2025-12-09
更新时间: 2025-12-09 14:39:15
行政区数: 35
```

### 使用配置

```python
manager = GeoDataManager()

# 获取配置信息
config_info = manager.get_config_info()
# 输出: {'version': '2025-12-09', 'last_updated': '2025-12-09 14:39:15', 'count': 35}

# 获取行政区划代码
adcode = manager.get_adcode("安徽省")
# 输出: 340000

# 获取所有省份
provinces = manager.get_available_provinces()
# 输出: ['中国', '安徽省', '北京市', ...]
```
