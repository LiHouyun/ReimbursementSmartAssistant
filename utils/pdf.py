
import os
import json
import pdfplumber
import re
from typing import Dict, Any, Optional, List

def extract_invoice_info(pdf_path: str) -> Optional[Dict[str, Any]]:
    """
    从中国PDF发票文件中提取关键信息
    """
    try:
        # 提取PDF文本内容
        text_content = extract_text_from_pdf(pdf_path)
        if not text_content:
            return None
        
        # 提取各项信息
        invoice_info = {
            "发票类型": extract_invoice_type(text_content),
            "发票号码": extract_invoice_number(text_content),
            "开票日期": extract_invoice_date(text_content),
            "购买方信息": extract_buyer_info(text_content),
            "销售方信息": extract_seller_info(text_content),
            "服务类型": extract_service_type(text_content),
            "项目明细": extract_item_details(text_content),
            "金额信息": extract_amount_info(text_content),
            "税率和税额": extract_tax_info(text_content),
            "价税合计": extract_total_amount(text_content),
            "出行信息": extract_travel_info(text_content),
            "开票人": extract_drawer(text_content),
            "备注": extract_remarks(text_content)
        }
        
        # 清理空值
        invoice_info = {k: v for k, v in invoice_info.items() if v is not None and v != {} and v != []}
        
        return invoice_info
        
    except Exception as e:
        print(f"处理PDF时发生错误: {e}")
        return None

def extract_text_from_pdf(pdf_path: str) -> str:
    """从PDF文件中提取文本内容"""
    text_content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
        return text_content
    except Exception as e:
        print(f"读取PDF文件失败: {e}")
        return ""

def extract_invoice_type(text: str) -> Optional[str]:
    """提取发票类型"""
    patterns = [
        r"电子发票（普通发票）",
        r"增值税专用发票",
        r"增值税（专用发票）",
        r"增值税普通发票",
        r"机动车销售统一发票"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return "电子发票（普通发票）"

def extract_invoice_number(text: str) -> Optional[str]:
    """提取发票号码"""
    patterns = [
        r"发票号码[:：]\s*(\d{20})",
        r"发票号码\s*(\d{20})",
        r"号码[:：]\s*(\d{20})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def extract_invoice_date(text: str) -> Optional[str]:
    """提取开票日期"""
    patterns = [
        r"开票日期[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
        r"开票日期[:：]\s*(\d{4}-\d{1,2}-\d{1,2})",
        r"日期[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
            return date_str
    return None

def extract_buyer_info(text: str) -> Dict[str, str]:
    """提取购买方信息"""
    buyer_info = {}
    
    # 更精确的购买方名称匹配
    name_patterns = [
        r"购\s*名称：\s*([^\n销]+?)(?=\s*(?:统一社会信用代码|纳税人识别号|销|$))",
        r"购买方[:：]\s*名称[:：]?\s*([^\n]+?)(?=\s*(?:统一社会信用代码|纳税人识别号|销|$))"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            buyer_info["名称"] = match.group(1).strip()
            break
    
    # 更精确的纳税人识别号匹配
    tax_id_patterns = [
        r"统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18,20})(?=\s*[^\n]*销)",
        r"统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18,20})(?=\s*[^\n]*售)",
        r"纳税人识别号[:：]\s*([A-Z0-9]{18,20})(?=\s*销售方)"
    ]
    for pattern in tax_id_patterns:
        match = re.search(pattern, text)
        if match:
            buyer_info["纳税人识别号"] = match.group(1).strip()
            break
    
    return buyer_info if buyer_info else {}

def extract_seller_info(text: str) -> Dict[str, str]:
    """提取销售方信息"""
    seller_info = {}
    
    # 更精确的销售方名称匹配
    name_patterns = [
        r"销\s*名称：\s*([^\n]+?)(?=\s*(?:统一社会信用代码|纳税人识别号|$))",
        r"销售方[:：]\s*名称[:：]?\s*([^\n]+?)(?=\s*(?:统一社会信用代码|纳税人识别号|$))"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            seller_info["名称"] = match.group(1).strip()
            break
    
    # 更精确的销售方纳税人识别号匹配
    tax_id_patterns = [
        r"(?<=售方信息).*?统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18,20})",
        r"统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18,20})(?=\s*[^\n]*项目名称)",
        r"(?<=售).*?统一社会信用代码/纳税人识别号[:：]\s*([A-Z0-9]{18,20})"
    ]
    for pattern in tax_id_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            seller_info["纳税人识别号"] = match.group(1).strip()
            break
    
    return seller_info if seller_info else {}

def extract_service_type(text: str) -> Optional[str]:
    """提取服务类型"""
    patterns = [
        r"旅客运输服务",
        r"运输服务",
        r"客运服务"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_item_details(text: str) -> List[Dict[str, str]]:
    """提取项目明细"""
    items = []
    
    # 使用更精确的表格解析
    lines = text.split('\n')
    table_start = False
    
    for i, line in enumerate(lines):
        if "项目名称" in line and "单价" in line and "数量" in line:
            table_start = True
            continue
        
        if table_start:
            if "合 计" in line or "价税合计" in line or not line.strip():
                break
            
            # 更精确的项目行匹配
            item_match = re.match(r'([^*\n]+)\s+(-?\d+\.\d{2})\s+(-?\d+\.\d{2})\s+(-?\d+\.\d{2})\s+([\d%\.]+)\s+(-?\d+\.\d{2})', line.strip())
            if item_match:
                item = {
                    "项目名称": item_match.group(1).strip(),
                    "单价": item_match.group(2),
                    "数量": item_match.group(3),
                    "金额": item_match.group(4),
                    "税率": item_match.group(5),
                    "税额": item_match.group(6)
                }
                items.append(item)
    
    return items

def extract_amount_info(text: str) -> Dict[str, str]:
    """提取金额信息"""
    amount_info = {}
    
    # 更精确的合计金额匹配
    patterns = [
        r"合 计\s+[￥¥]?\s*(\d+\.\d{2})",
        r"合计金额\s+[￥¥]?\s*(\d+\.\d{2})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_info["合计金额"] = match.group(1)
            break
    
    return amount_info if amount_info else {}

def extract_tax_info(text: str) -> Dict[str, str]:
    """提取税率和税额信息"""
    tax_info = {}
    
    # 更精确的合计税额匹配
    tax_patterns = [
        r"合 计\s+[￥¥]?\s*\d+\.\d{2}\s+[￥¥]?\s*(\d+\.\d{2})",
        r"合计税额\s+[￥¥]?\s*(\d+\.\d{2})"
    ]
    
    for pattern in tax_patterns:
        match = re.search(pattern, text)
        if match:
            tax_info["合计税额"] = match.group(1)
            break
    
    return tax_info if tax_info else {}

def extract_total_amount(text: str) -> Dict[str, str]:
    """提取价税合计"""
    total_info = {}
    
    # 小写金额 - 更精确匹配
    patterns = [
        r"价税合计[（(]小写[)）][\s￥¥]*([\d,]+\.\d{2})",
        r"小写[)）]?[\s￥¥]*([\d,]+\.\d{2})",
        r"¥\s*(\d+\.\d{2})(?=\s*备)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            total_info["小写"] = match.group(1)
            break
    
    # 大写金额 - 更精确匹配
    chinese_patterns = [
        r"价税合计（大写）\s*([零壹贰叁肆伍陆柒捌玖拾佰仟万亿圆角分整]+)(?=\s*[（(]小写[)）])",
        r"（大写）\s*([零壹贰叁肆伍陆柒捌玖拾佰仟万亿圆角分整]+)"
    ]
    
    for pattern in chinese_patterns:
        chinese_match = re.search(pattern, text)
        if chinese_match:
            total_info["大写"] = chinese_match.group(1)
            break
    
    return total_info if total_info else {}

def extract_travel_info(text: str) -> Dict[str, str]:
    """提取出行信息"""
    travel_info = {}
    
    lines = text.split('\n')
    header_found = False
    
    for i, line in enumerate(lines):
        if "出行人" in line and "有效身份证件号" in line:
            header_found = True
            continue
        
        if header_found and line.strip() and not any(x in line for x in ["出行人", "有效身份证件号", "价税合计"]):
            travel_data = re.split(r'\s+', line.strip())
            if len(travel_data) >= 6:
                travel_info = {
                    "出行人": travel_data[0],
                    "有效身份证件号": travel_data[1],
                    "出行日期": travel_data[2],
                    "出发地": travel_data[3],
                    "到达地": travel_data[4],
                    "交通工具类型": travel_data[5] if len(travel_data) > 5 else ""
                }
            break
    
    return travel_info if travel_info else {}

def extract_drawer(text: str) -> Optional[str]:
    """提取开票人"""
    patterns = [
        r"开票人[:：]\s*([^\n]+?)(?=\s*(?:didi|$))",
        r"开票人\s*([^\n]+?)(?=\s*(?:didi|$))"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def extract_remarks(text: str) -> Optional[str]:
    """提取备注信息"""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if "备注" in line and i + 1 < len(lines):
            remark_line = lines[i + 1].strip()
            if remark_line and remark_line != "didi":
                return remark_line
    return None

# 使用示例
if __name__ == "__main__":
    # 示例用法
    file_path = "./test/test_files"
    json_file_path = f"{file_path}/invoice_info.json"
    pdf_file_path = f"{file_path}/3.pdf"  # 替换为你的PDF文件路径
    
    invoice_data = extract_invoice_info(pdf_file_path)
    
    if invoice_data:
        # 转换为JSON格式
        json_output = json.dumps(invoice_data, ensure_ascii=False, indent=2)
        print("提取的发票信息:")
        print(json_output)
        
        # 保存到文件
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(invoice_data, f, ensure_ascii=False, indent=2)
        print("信息已保存到 invoice_info.json")

        total_amount = invoice_data['价税合计']['小写']
        date_4 = invoice_data['开票日期'].replace('-', '')[4:8]
        print(total_amount)
        print(invoice_data['开票日期'].replace('-', '')[4:8])

        # 把 pdf_file_path 重命名为 “total_amount date_4”
        os.rename(pdf_file_path, f"{file_path}/{total_amount} {date_4}.pdf") 

    else:
        print("未能成功提取发票信息")
