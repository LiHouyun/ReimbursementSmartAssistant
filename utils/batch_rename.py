import os

import os
import json
from typing import List, Dict

def _check_for_duplicates(new_name_list: List[str]) -> Dict[str, List[int]]:
    """检查新文件名列表中的重复项"""
    name_indices = {}
    for idx, name in enumerate(new_name_list):
        if name not in name_indices:
            name_indices[name] = []
        name_indices[name].append(idx)
    
    # 筛选出有重复的文件名
    duplicates = {name: indices for name, indices in name_indices.items() if len(indices) > 1}
    return duplicates

def _resolve_name_conflicts(src_list: List[str], new_name_list: List[str]) -> (List[str], List[Dict]):
    """
    处理不同文件重命名后名称相同的冲突
    返回处理后的新文件名列表和冲突信息
    """
    duplicates = _check_for_duplicates(new_name_list)
    conflict_info = []
    resolved_names = new_name_list.copy()
    
    for name, indices in duplicates.items():
        # 记录冲突信息
        conflict_files = [os.path.basename(src_list[i]) for i in indices]
        conflict_entry = {
            "conflict_type": "name_collision",
            "original_files": conflict_files,
            "original_target": name,
            "resolved_names": []
        }
        
        # 为重复的文件名添加递增后缀
        for i, idx in enumerate(indices):
            if i == 0:
                # 第一个文件保持原名称
                conflict_entry["resolved_names"].append(name)
                continue
                
            # 分离文件名和扩展名
            base, ext = os.path.splitext(name)
            new_name = f"{base}_{i+1}{ext}"
            resolved_names[idx] = new_name
            conflict_entry["resolved_names"].append(new_name)
        
        conflict_info.append(conflict_entry)
        print(f"命名冲突处理: 文件 {', '.join(conflict_files)} 重命名后将相同，已添加后缀处理")
    
    return resolved_names, conflict_info

def _resolve_swap_conflicts(src_list: List[str], new_name_list: List[str]) -> (List[str], List[Dict]):
    """
    处理文件交换式冲突 (A→B 且 B→A)
    返回处理后的新文件名列表和冲突信息
    """
    swap_conflicts = []
    temp_suffix = ".tmp_rename"
    processed = set()
    
    # 先检查是否存在交换冲突
    for i in range(len(src_list)):
        if i in processed:
            continue
            
        src_file = os.path.basename(src_list[i])
        target_name = new_name_list[i]
        
        # 查找是否有文件以当前目标名为源文件，并以当前源文件名为目标
        for j in range(len(src_list)):
            if i == j or j in processed:
                continue
                
            other_src = os.path.basename(src_list[j])
            other_target = new_name_list[j]
            
            if other_src == target_name and other_target == src_file:
                swap_conflicts.append((i, j))
                processed.add(i)
                processed.add(j)
                break
    
    # 处理交换冲突
    conflict_info = []
    resolved_names = new_name_list.copy()
    
    for i, j in swap_conflicts:
        src_i = src_list[i]
        src_j = src_list[j]
        target_i = new_name_list[i]
        target_j = new_name_list[j]
        
        # 创建临时文件名
        temp_i = f"{target_i}{temp_suffix}"
        temp_j = f"{target_j}{temp_suffix}"
        
        # 更新临时文件名
        resolved_names[i] = temp_i
        resolved_names[j] = temp_j
        
        # 记录冲突信息
        conflict_entry = {
            "conflict_type": "file_swap",
            "original_files": [os.path.basename(src_i), os.path.basename(src_j)],
            "original_targets": [target_i, target_j],
            "temporary_names": [temp_i, temp_j],
            "final_targets": [target_i, target_j]
        }
        conflict_info.append(conflict_entry)
        print(f"交换冲突处理: 文件 {os.path.basename(src_i)} 与 {os.path.basename(src_j)} 将互换名称，已使用临时文件处理")
    
    return resolved_names, conflict_info

def _finalize_swap_files(src_list: List[str], original_new_names: List[str], swap_conflicts: List[Dict]):
    """完成交换冲突文件的最终重命名"""
    for conflict in swap_conflicts:
        if conflict["conflict_type"] != "file_swap":
            continue
            
        # 找到对应的源文件索引
        indices = []
        for file in conflict["original_files"]:
            for i, src in enumerate(src_list):
                if os.path.basename(src) == file:
                    indices.append(i)
                    break
        
        if len(indices) != 2:
            continue
            
        i, j = indices
        src_i = src_list[i]
        src_j = src_list[j]
        
        # 获取临时文件路径
        folder_i = os.path.dirname(src_i)
        folder_j = os.path.dirname(src_j)
        
        temp_i_path = os.path.join(folder_i, conflict["temporary_names"][0])
        temp_j_path = os.path.join(folder_j, conflict["temporary_names"][1])
        
        # 最终重命名
        final_i_path = os.path.join(folder_i, conflict["final_targets"][0])
        final_j_path = os.path.join(folder_j, conflict["final_targets"][1])
        
        os.rename(temp_i_path, final_i_path)
        os.rename(temp_j_path, final_j_path)
        
        print(f"完成交换: {temp_i_path} -> {final_i_path}")
        print(f"完成交换: {temp_j_path} -> {final_j_path}")

def batch_rename(src_list: List[str], new_name_list: List[str]) -> str:
    """
    批量重命名文件，处理命名冲突和交换场景
    
    :param src_list: 原文件路径列表
    :param new_name_list: 新文件名列表
    :return: JSON字符串，包含重命名结果和冲突信息
    """
    result = {
        "success": True,
        "total_files": len(src_list),
        "renamed_files": [],
        "failed_files": [],
        "conflicts": []
    }
    
    # 基本检查
    if len(src_list) != len(new_name_list):
        result["success"] = False
        result["error"] = "源文件列表和新文件名列表长度不一致！"
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # 检查文件是否存在
    for src in src_list:
        if not os.path.isfile(src):
            result["success"] = False
            result["failed_files"].append({
                "source": src,
                "reason": "文件不存在"
            })
    
    if result["failed_files"]:
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # 处理命名冲突（不同文件重命名后名称相同）
    resolved_names, name_conflicts = _resolve_name_conflicts(src_list, new_name_list)
    result["conflicts"].extend(name_conflicts)
    
    # 处理交换冲突（A→B 且 B→A）
    resolved_names, swap_conflicts = _resolve_swap_conflicts(src_list, resolved_names)
    result["conflicts"].extend(swap_conflicts)
    
    # 执行第一次重命名（处理普通文件和交换冲突的临时文件）
    for src, new_name in zip(src_list, resolved_names):
        try:
            folder = os.path.dirname(src)
            dst = os.path.join(folder, new_name)
            os.rename(src, dst)
            
            result["renamed_files"].append({
                "source": src,
                "temporary_destination": dst if any(
                    c["conflict_type"] == "file_swap" and os.path.basename(src) in c["original_files"] 
                    for c in swap_conflicts
                ) else None,
                "final_destination": dst if not any(
                    c["conflict_type"] == "file_swap" and os.path.basename(src) in c["original_files"]
                    for c in swap_conflicts
                ) else None
            })
        except Exception as e:
            result["success"] = False
            result["failed_files"].append({
                "source": src,
                "reason": f"重命名失败: {str(e)}"
            })
    
    # 完成交换冲突文件的最终重命名
    if swap_conflicts:
        _finalize_swap_files(src_list, new_name_list, swap_conflicts)
        
        # 更新结果中的最终目标路径
        for conflict in swap_conflicts:
            for i, file in enumerate(conflict["original_files"]):
                for item in result["renamed_files"]:
                    if os.path.basename(item["source"]) == file:
                        item["final_destination"] = os.path.join(
                            os.path.dirname(item["source"]), 
                            conflict["final_targets"][i]
                        )
                        break
    
    return json.dumps(result, ensure_ascii=False, indent=2)

def format_rename_message(result_json: str) -> str:
    """
    将批量重命名的JSON结果转换为前端展示的说明文本
    
    :param result_json: 批量重命名函数返回的JSON字符串
    :return: 格式化后的说明文本
    """
    try:
        result = json.loads(result_json)
    except json.JSONDecodeError:
        return "处理结果解析失败，请重试"
    
    messages = []
    total = result.get("total_files", 0)
    success_count = len(result.get("renamed_files", []))
    failed_count = len(result.get("failed_files", []))
    
    # 总体处理情况
    if result.get("success", False):
        messages.append(f"批量重命名完成！共处理{total}个文件，全部成功。")
    else:
        messages.append(f"批量重命名已完成，但存在问题：共处理{total}个文件，成功{success_count}个，失败{failed_count}个。")
    
    # 冲突处理说明
    conflicts = result.get("conflicts", [])
    if conflicts:
        messages.append("\n【冲突处理详情】")
        for i, conflict in enumerate(conflicts, 1):
            if conflict["conflict_type"] == "name_collision":
                original_files = ", ".join(conflict["original_files"])
                original_target = conflict["original_target"]
                resolved = ", ".join(conflict["resolved_names"])
                messages.append(f"{i}. 命名冲突：文件 {original_files} 按规则将重命名为相同的 {original_target}，已自动处理为：{resolved}")
            
            elif conflict["conflict_type"] == "file_swap":
                original_files = ", ".join(conflict["original_files"])
                final_targets = ", ".join(conflict["final_targets"])
                messages.append(f"{i}. 文件交换：文件 {original_files} 需要互换名称，已通过临时文件安全处理，最终命名为：{final_targets}")
    
    # 失败文件说明
    failed_files = result.get("failed_files", [])
    if failed_files:
        messages.append("\n【处理失败文件】")
        for i, file in enumerate(failed_files, 1):
            messages.append(f"{i}. {file['source']}：{file['reason']}")
    
    # 成功文件摘要
    if success_count > 0 and (conflicts or failed_files):  # 只有存在问题时才显示成功摘要
        messages.append("\n【成功重命名文件】")
        # 只显示前3个成功文件，避免信息过长
        shown = 0
        for file in result["renamed_files"]:
            if shown >= 3:
                remaining = len(result["renamed_files"]) - 3
                messages.append(f"还有{remaining}个文件成功重命名...")
                break
            dest = file["final_destination"] or file["temporary_destination"]
            messages.append(f"{os.path.basename(file['source'])} → {os.path.basename(dest)}")
            shown += 1
    
    return "\n".join(messages)


if __name__ == "__main__":
    src_files = [
        r"/path/to/file1.txt",
        r"/path/to/file2.jpg",
        r"/path/to/file3.pdf"
    ]

    new_names = [
        "new1.txt",
        "new1.jpg",
        "new3.pdf"
    ]

    print(batch_rename(src_files, new_names))
