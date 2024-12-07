import av
import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import json
import argparse

'''
# 基本使用
python check_videos.py /path/to/videos --remove --savelog
'''

def check_video_av(video_path):
    """检查单个视频文件是否可以用 PyAV 正常读取"""
    try:
        container = av.open(str(video_path))
        # 尝试读取一帧
        for frame in container.decode(video=0):
            break
        container.close()
        return True, None
    except Exception as e:
        return False, str(e)

def scan_video_files(root_dir):
    """扫描目录下的所有视频文件"""
    video_extensions = {'.avi', '.mp4', '.mov', '.mkv'}
    video_files = []
    
    for path in Path(root_dir).rglob('*'):
        if path.suffix.lower() in video_extensions:
            video_files.append(str(path))
    
    return video_files

def check_videos(video_path, max_workers=8, remove=False, savelog=False):
    """主函数：检查所有视频文件
    Args:
        video_path: 视频目录路径
        max_workers: 线程池大小
        remove: 是否删除无法读取的视频
        savelog: 是否保存检查结果到json文件
    """
    print(f"开始扫描目录: {video_path}")
    video_files = scan_video_files(video_path)
    total_files = len(video_files)
    print(f"找到 {total_files} 个视频文件")

    results = {
        'success': [],
        'failed': []
    }
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, video_file in enumerate(video_files, 1):
            success, error = check_video_av(video_file)
            
            if success:
                results['success'].append(video_file)
            else:
                results['failed'].append({
                    'file': video_file,
                    'error': error
                })
            
            # 打印进度
            if i % 10 == 0 or i == total_files:
                elapsed_time = time.time() - start_time
                print(f"进度: {i}/{total_files} ({i/total_files*100:.2f}%) "
                      f"耗时: {elapsed_time:.2f}秒")

    # 保存结果到文件
    if savelog:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = f"video_check_results_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"详细结果已保存到: {result_file}")

    # 打印统计信息
    print("\n检查完成!")
    print(f"成功读取: {len(results['success'])} 个文件")
    print(f"读取失败: {len(results['failed'])} 个文件")

    # 如果有失败的文件，打印它们并选择性删除
    if results['failed']:
        print("\n失败的文件列表:")
        for fail in results['failed']:
            print(f"\n文件: {fail['file']}")
            print(f"错误: {fail['error']}")
            if remove:
                try:
                    os.remove(fail['file'])
                    print(f"已删除: {fail['file']}")
                except Exception as e:
                    print(f"删除失败: {fail['file']}, 错误: {str(e)}")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='检查视频文件是否可以正常读取')
    parser.add_argument('video_dir', type=str, help='视频文件目录路径')
    parser.add_argument('--remove', action='store_true', 
                        help='是否删除无法读取的视频文件')
    parser.add_argument('--max-workers', type=int, default=8,
                        help='最大线程数 (默认: 8)')
    parser.add_argument('--savelog', action='store_true',
                        help='是否保存检查结果到json文件')
    
    args = parser.parse_args()
    
    # 运行检查
    check_videos(args.video_dir, args.max_workers, args.remove, args.savelog)