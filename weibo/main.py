#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微博搜索爬虫主程序

用法:
    python main.py                    # 使用默认配置运行
    python main.py --keywords "关键词1,关键词2"  # 指定关键词
    python main.py --start-date 2024-01-01 --end-date 2024-01-31  # 指定日期范围
"""

import argparse
import sys
import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='微博搜索爬虫')
    
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        help='搜索关键词，多个关键词用逗号分隔，例如: "迪丽热巴,杨幂"'
    )
    
    parser.add_argument(
        '--keyword-file', '-f',
        type=str,
        help='包含关键词的文件路径，每行一个关键词'
    )
    
    parser.add_argument(
        '--start-date', '-s',
        type=str,
        help='搜索开始日期，格式: YYYY-MM-DD，例如: 2024-01-01'
    )
    
    parser.add_argument(
        '--end-date', '-e',
        type=str,
        help='搜索结束日期，格式: YYYY-MM-DD，例如: 2024-01-31'
    )
    
    parser.add_argument(
        '--weibo-type', '-t',
        type=int,
        choices=[0, 1, 2, 3, 4, 5, 6],
        help='微博类型: 0-全部 1-原创 2-热门 3-关注人 4-认证用户 5-媒体 6-观点'
    )
    
    parser.add_argument(
        '--contain-type', '-c',
        type=int,
        choices=[0, 1, 2, 3, 4],
        help='内容类型: 0-不筛选 1-包含图片 2-包含视频 3-包含音乐 4-包含短链接'
    )
    
    parser.add_argument(
        '--region', '-r',
        type=str,
        help='地区筛选，例如: "北京,上海" 或 "全部"'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='爬取结果数量限制，0表示不限制'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        help='请求延迟时间（秒），避免被封'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='输出目录路径'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='ERROR',
        help='日志级别'
    )
    
    return parser.parse_args()


def validate_date(date_string):
    """验证日期格式"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_arguments(args):
    """验证命令行参数"""
    errors = []
    
    # 验证日期格式
    if args.start_date and not validate_date(args.start_date):
        errors.append(f"开始日期格式错误: {args.start_date}，请使用 YYYY-MM-DD 格式")
    
    if args.end_date and not validate_date(args.end_date):
        errors.append(f"结束日期格式错误: {args.end_date}，请使用 YYYY-MM-DD 格式")
    
    # 验证日期逻辑
    if args.start_date and args.end_date:
        start = datetime.strptime(args.start_date, '%Y-%m-%d')
        end = datetime.strptime(args.end_date, '%Y-%m-%d')
        if start > end:
            errors.append("开始日期不能晚于结束日期")
    
    # 验证关键词文件
    if args.keyword_file and not os.path.isfile(args.keyword_file):
        errors.append(f"关键词文件不存在: {args.keyword_file}")
    
    # 验证输出目录
    if args.output_dir and not os.path.isdir(args.output_dir):
        try:
            os.makedirs(args.output_dir, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建输出目录 {args.output_dir}: {e}")
    
    if errors:
        print("参数验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def update_settings_from_args(settings, args):
    """根据命令行参数更新设置"""
    
    # 更新关键词
    if args.keywords:
        keyword_list = [kw.strip() for kw in args.keywords.split(',') if kw.strip()]
        settings.set('KEYWORD_LIST', keyword_list)
        print(f"使用关键词: {keyword_list}")
    elif args.keyword_file:
        settings.set('KEYWORD_LIST', args.keyword_file)
        print(f"使用关键词文件: {args.keyword_file}")
    
    # 更新日期范围
    if args.start_date:
        settings.set('START_DATE', args.start_date)
        print(f"搜索开始日期: {args.start_date}")
    
    if args.end_date:
        settings.set('END_DATE', args.end_date)
        print(f"搜索结束日期: {args.end_date}")
    
    # 更新微博类型
    if args.weibo_type is not None:
        settings.set('WEIBO_TYPE', args.weibo_type)
        type_names = {0: '全部', 1: '原创', 2: '热门', 3: '关注人', 4: '认证用户', 5: '媒体', 6: '观点'}
        print(f"微博类型: {type_names.get(args.weibo_type, '未知')}")
    
    # 更新内容类型
    if args.contain_type is not None:
        settings.set('CONTAIN_TYPE', args.contain_type)
        contain_names = {0: '不筛选', 1: '包含图片', 2: '包含视频', 3: '包含音乐', 4: '包含短链接'}
        print(f"内容类型: {contain_names.get(args.contain_type, '未知')}")
    
    # 更新地区
    if args.region:
        region_list = [r.strip() for r in args.region.split(',') if r.strip()]
        settings.set('REGION', region_list)
        print(f"地区筛选: {region_list}")
    
    # 更新数量限制
    if args.limit is not None:
        settings.set('LIMIT_RESULT', args.limit)
        print(f"数量限制: {args.limit if args.limit > 0 else '无限制'}")
    
    # 更新请求延迟
    if args.delay is not None:
        settings.set('DOWNLOAD_DELAY', args.delay)
        print(f"请求延迟: {args.delay}秒")
    
    # 更新输出目录
    if args.output_dir:
        settings.set('IMAGES_STORE', args.output_dir)
        settings.set('FILES_STORE', args.output_dir)
        print(f"输出目录: {args.output_dir}")
    
    # 更新日志级别
    settings.set('LOG_LEVEL', args.log_level)
    if args.log_level != 'ERROR':
        print(f"日志级别: {args.log_level}")


def print_config_summary(settings):
    """打印配置摘要"""
    print("\n" + "="*50)
    print("微博搜索爬虫配置摘要")
    print("="*50)
    
    # 获取关键词
    keyword_list = settings.get('KEYWORD_LIST', [])
    if isinstance(keyword_list, str):
        print(f"关键词文件: {keyword_list}")
    else:
        print(f"关键词: {', '.join(keyword_list) if keyword_list else '未设置'}")
    
    # 日期范围
    start_date = settings.get('START_DATE', '未设置')
    end_date = settings.get('END_DATE', '未设置')
    print(f"日期范围: {start_date} 至 {end_date}")
    
    # 微博类型
    weibo_type = settings.get('WEIBO_TYPE', 0)
    type_names = {0: '全部微博', 1: '原创微博', 2: '热门微博', 3: '关注人微博', 4: '认证用户微博', 5: '媒体微博', 6: '观点微博'}
    print(f"微博类型: {type_names.get(weibo_type, '未知')}")
    
    # 内容类型
    contain_type = settings.get('CONTAIN_TYPE', 0)
    contain_names = {0: '不筛选', 1: '包含图片', 2: '包含视频', 3: '包含音乐', 4: '包含短链接'}
    print(f"内容筛选: {contain_names.get(contain_type, '未知')}")
    
    # 地区
    region = settings.get('REGION', ['全部'])
    print(f"地区: {', '.join(region) if isinstance(region, list) else region}")
    
    # 数量限制
    limit = settings.get('LIMIT_RESULT', 0)
    print(f"数量限制: {'无限制' if limit == 0 else f'{limit}条'}")
    
    # 请求延迟
    delay = settings.get('DOWNLOAD_DELAY', 10)
    print(f"请求延迟: {delay}秒")
    
    print("="*50)


def main():
    """主函数"""
    print("微博搜索爬虫启动中...")
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 验证参数
    validate_arguments(args)
    
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 根据命令行参数更新设置
        update_settings_from_args(settings, args)
        
        # 打印配置摘要
        print_config_summary(settings)
        
        # 检查必要的配置
        keyword_list = settings.get('KEYWORD_LIST')
        if not keyword_list:
            print("\n错误: 未设置搜索关键词")
            print("请使用 --keywords 参数指定关键词，或使用 --keyword-file 指定关键词文件")
            print("例如: python main.py --keywords '迪丽热巴,杨幂'")
            sys.exit(1)
        
        # 确认开始爬取
        print(f"\n准备开始爬取...")
        print("按 Ctrl+C 可随时停止爬虫")
        
        # 创建并启动爬虫进程
        process = CrawlerProcess(settings)
        process.crawl('search')  # 'search' 是爬虫的名称
        process.start()  # 阻塞直到爬虫完成
        
        print("\n爬虫已完成!")
        
    except KeyboardInterrupt:
        print("\n\n用户中断，爬虫已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n爬虫运行时发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
