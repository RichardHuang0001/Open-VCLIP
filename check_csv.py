import pandas as pd
import os
from pathlib import Path
import argparse
import time

'''
# 基本使用
python check_csv.py /path/to/dataset test.csv --remove --savelog

参数说明：
- 第一个参数是数据集根目录路径
- 第二个参数是CSV文件路径
- --remove：是否从CSV中删除不存在的条目
- --savelog：是否保存检查结果到json文件
'''

def check_paths(dataset_root, csv_path, remove=False, savelog=False):
    """检查CSV文件中的视频路径是否存在
    
    Args:
        dataset_root: 数据集根目录路径
        csv_path: CSV文件路径
        remove: 是否删除不存在的条目
        savelog: 是否保存检查结果到json文件
    """
    print(f"开始检查CSV文件: {csv_path}")
    
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_path, header=None)
        total_entries = len(df)
        print(f"共读取到 {total_entries} 条记录")
    except Exception as e:
        print(f"读取CSV文件失败: {str(e)}")
        return

    # 存储结果
    results = {
        'existing': [],
        'missing': []
    }
    
    start_time = time.time()
    
    # 检查每个文件路径
    for idx, row in df.iterrows():
        video_path = row[0].split(',')[0]  # 分割并获取文件路径部分
        full_path = os.path.join(dataset_root, video_path)
        
        if os.path.exists(full_path):
            results['existing'].append(video_path)
        else:
            results['missing'].append(video_path)
            
        # 打印进度
        if (idx + 1) % 100 == 0 or (idx + 1) == total_entries:
            elapsed_time = time.time() - start_time
            print(f"进度: {idx+1}/{total_entries} ({(idx+1)/total_entries*100:.2f}%) "
                  f"耗时: {elapsed_time:.2f}秒")

    # 打印统计信息
    print("\n检查完成!")
    print(f"存在的文件: {len(results['existing'])} 个")
    print(f"缺失的文件: {len(results['missing'])} 个")

    # 如果有缺失的文件，打印它们
    if results['missing']:
        print("\n缺失的文件列表:")
        for path in results['missing']:
            print(path)

    # 保存结果到json
    if savelog:
        import json
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = f"path_check_results_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n详细结果已保存到: {result_file}")

    # 如果需要删除缺失的条目
    if remove and results['missing']:
        print("\n正在从CSV中删除缺失的条目...")
        # 创建一个布尔掩码，标记要保留的行
        mask = df[0].apply(lambda x: x.split(',')[0] in results['existing'])
        # 直接覆盖原CSV文件
        df[mask].to_csv(csv_path, header=False, index=False)
        print(f"已更新原CSV文件: {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='检查CSV文件中的视频路径是否存在')
    parser.add_argument('dataset_root', type=str, help='数据集根目录路径')
    parser.add_argument('csv_path', type=str, help='CSV文件路径')
    parser.add_argument('--remove', action='store_true', 
                        help='是否删除不存在的条目并创建新的CSV文件')
    parser.add_argument('--savelog', action='store_true',
                        help='是否保存检查结果到json文件')
    
    args = parser.parse_args()
    
    check_paths(args.dataset_root, args.csv_path, args.remove, args.savelog)