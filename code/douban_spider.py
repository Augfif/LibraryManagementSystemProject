"""
豆瓣图书爬虫集成模块
用于图书管理系统集成豆瓣图书爬虫功能
"""

import random
import time
import sqlite3
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple

import requests
import pandas as pd
from bs4 import BeautifulSoup


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Tag:
    """标签数据类"""
    name: str
    url: str


@dataclass
class BookInfo:
    """图书信息数据类（映射到系统字段）"""
    bookname: str = ""
    price: str = ""
    author: str = ""
    stock: int = 10
    pubcom: str = ""
    
    # 源数据
    source_data: Dict = field(default_factory=dict)


# 配置类
class SpiderConfig:
    """爬虫配置"""
    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = BASE_DIR / "爬虫"
    TAG_HTML_PATH: Path = CACHE_DIR / "douban_book_tag" / "douban_book_all_tag.html"
    LIST_HTML_DIR: Path = CACHE_DIR / "douban_book_data_dagai"
    DETAIL_HTML_DIR: Path = CACHE_DIR / "douban_book_data_detail"
    CSV_OUTPUT_DIR: Path = CACHE_DIR / "data_csv"
    
    # 数据库路径（导入时使用）
    BOOK_DB_PATH: Path = BASE_DIR / "user_data" / "book_info.db"
    
    # 字段映射配置
    FIELD_MAPPING: Dict = {
        "bookname": "title",
        "price": "price",
        "author": "author",
        "stock": 10,
        "pubcom": "publisher"
    }
    
    # 请求配置
    REQUEST_DELAY_MIN: float = 0.1
    REQUEST_DELAY_MAX: float = 2.0
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 10
    
    # User-Agent 列表
    USER_AGENTS: List = field(default_factory=list)
    
    def __init__(self):
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2040.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
        ]


config = SpiderConfig()


def get_request(url: str, **kwargs) -> Optional[requests.Response]:
    """
    发送HTTP请求（带反爬策略）
    
    Args:
        url: 请求URL
        **kwargs: 其他请求参数
        
    Returns:
        Response对象或None
    """
    delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
    logger.info(f"请求URL: {url}, 等待 {delay:.2f} 秒")
    time.sleep(delay)
    
    headers = {
        'User-Agent': random.choice(config.USER_AGENTS)
    }
    
    for attempt in range(config.MAX_RETRIES):
        try:
            response = requests.get(
                url=url, 
                timeout=config.REQUEST_TIMEOUT, 
                headers=headers, 
                **kwargs
            )
            if response.status_code == 200:
                return response
            else:
                logger.warning(f"请求失败，状态码: {response.status_code}，重试 {attempt + 1}/{config.MAX_RETRIES}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"请求异常: {e}，重试 {attempt + 1}/{config.MAX_RETRIES}")
        
        if attempt < config.MAX_RETRIES - 1:
            time.sleep(random.uniform(1, 2))
    
    logger.error("多次请求失败")
    return None


def save_html_file(file_path: Path, content: str) -> None:
    """保存HTML文件"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as fp:
        fp.write(str(content))
    logger.info(f"已保存: {file_path}")


def load_html_file(file_path: Path) -> Optional[str]:
    """加载HTML文件"""
    if not file_path.exists():
        return None
    with open(file_path, 'r', encoding='utf-8') as fp:
        return fp.read()


def download_tags(force: bool = False) -> Path:
    """
    下载标签分类页面
    
    Args:
        force: 强制重新下载，即使文件已存在
        
    Returns:
        保存的文件路径
    """
    url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
    
    if not force and config.TAG_HTML_PATH.exists():
        logger.info(f"标签文件已存在: {config.TAG_HTML_PATH}")
        return config.TAG_HTML_PATH
    
    logger.info("正在下载标签页面...")
    response = get_request(url)
    if response is not None:
        save_html_file(config.TAG_HTML_PATH, response.text)
        return config.TAG_HTML_PATH
    else:
        raise Exception("标签页面下载失败")


def parse_tags_from_html(html_content: str) -> List[Tag]:
    """
    从HTML中解析标签列表
    
    Args:
        html_content: HTML内容
        
    Returns:
        标签列表
    """
    soup = BeautifulSoup(html_content, features='lxml')
    tags: List[Tag] = []
    
    tag_tables = soup.select('table.tagCol')
    for table in tag_tables:
        tag_links = table.select('a')
        for link in tag_links:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            if name and href:
                # 补全URL
                if href.startswith('/'):
                    href = f"https://book.douban.com{href}"
                tags.append(Tag(name=name, url=href))
    
    logger.info(f"解析出 {len(tags)} 个标签")
    return tags


def get_tags(force_download: bool = False) -> List[Tag]:
    """
    获取标签列表（优先使用缓存）
    
    Args:
        force_download: 强制重新下载
        
    Returns:
        标签列表
    """
    if force_download or not config.TAG_HTML_PATH.exists():
        download_tags(force=force_download)
    
    html_content = load_html_file(config.TAG_HTML_PATH)
    if html_content:
        return parse_tags_from_html(html_content)
    return []


def download_tag_list(tag_url: str, start: int = 0, force: bool = False) -> Optional[Path]:
    """
    下载指定标签的图书列表页
    
    Args:
        tag_url: 标签URL
        start: 起始位置
        force: 强制重新下载
        
    Returns:
        保存的文件路径
    """
    tag_name = tag_url.split('/')[-1] if tag_url else "unknown"
    file_name = f"douban_book_data_dagai_{tag_name}_{start}.html"
    file_path = config.LIST_HTML_DIR / file_name
    
    if not force and file_path.exists():
        logger.info(f"列表文件已存在: {file_path}")
        return file_path
    
    url = f"{tag_url}?start={start}&type=T"
    logger.info(f"下载列表页: {url}")
    
    response = get_request(url)
    if response is not None:
        save_html_file(file_path, response.text)
        return file_path
    return None


def parse_book_links_from_list_html(html_content: str) -> List[str]:
    """
    从列表页HTML解析图书详情页链接
    
    Args:
        html_content: 列表页HTML
        
    Returns:
        图书链接列表
    """
    soup = BeautifulSoup(html_content, features='lxml')
    links: List[str] = []
    
    items = soup.select('li.subject-item')
    for item in items:
        link_tag = item.select_one('a.nbg')
        if link_tag:
            href = link_tag.get('href', '')
            if href:
                links.append(href)
    
    logger.info(f"解析出 {len(links)} 个图书链接")
    return links


def download_book_detail(book_url: str, force: bool = False) -> Optional[Path]:
    """
    下载图书详情页
    
    Args:
        book_url: 图书URL
        force: 强制重新下载
        
    Returns:
        保存的文件路径
    """
    # 提取图书ID
    book_id = ""
    parts = book_url.split('/')
    for i, part in enumerate(parts):
        if part == 'subject' and i + 1 < len(parts):
            book_id = parts[i + 1]
            break
    
    if not book_id:
        logger.warning(f"无法从URL提取图书ID: {book_url}")
        return None
    
    file_name = f"douban_book_detail_{book_id}.html"
    file_path = config.DETAIL_HTML_DIR / file_name
    
    if not force and file_path.exists():
        logger.info(f"详情页已存在: {file_path}")
        return file_path
    
    logger.info(f"下载详情页: {book_url}")
    response = get_request(book_url)
    if response is not None:
        save_html_file(file_path, response.text)
        return file_path
    return None


def parse_book_from_detail_html(html_content: str, book_id: str) -> Optional[BookInfo]:
    """
    从详情页HTML解析图书信息
    
    Args:
        html_content: 详情页HTML
        book_id: 图书ID
        
    Returns:
        BookInfo对象
    """
    try:
        soup = BeautifulSoup(html_content, features='lxml')
        
        # 提取源数据
        source_data = {}
        
        # 书名
        title = ''
        tag_title = soup.select_one('#wrapper > h1 > span')
        if tag_title:
            title = tag_title.string.strip() if tag_title.string else ''
        source_data['title'] = title
        
        # 详细信息区域
        tag_subjectwrap = soup.select_one('#content > div > div.article > div.indent > div.subjectwrap.clearfix')
        if not tag_subjectwrap:
            return None
        
        tag_info = tag_subjectwrap.select_one('div.subject.clearfix > #info')
        if not tag_info:
            return None
        
        # 辅助函数：提取信息字段
        def get_info_value(tag_info, label):
            tag = tag_info.find(name='span', attrs={'class': 'pl'}, string=label)
            if tag is None:
                return ''
            try:
                next_sibling = tag.next_sibling
                if next_sibling and hasattr(next_sibling, 'next_sibling') and next_sibling.next_sibling:
                    return next_sibling.next_sibling.text.strip()
                elif next_sibling:
                    return next_sibling.strip()
            except:
                pass
            return ''
        
        # 提取字段
        author = get_info_value(tag_info, ' 作者')
        publisher = get_info_value(tag_info, '出版社:')
        
        tag_price = tag_info.find(name='span', attrs={'class': 'pl'}, string='定价:')
        price = tag_price.next_sibling.strip() if (tag_price and tag_price.next_sibling) else ''
        
        source_data['author'] = author
        source_data['publisher'] = publisher
        source_data['price'] = price
        
        # 映射到系统字段
        book = BookInfo(
            bookname=title,
            price=price,
            author=author,
            stock=config.FIELD_MAPPING['stock'],
            pubcom=publisher,
            source_data=source_data
        )
        
        logger.info(f"解析图书: {book.bookname}")
        return book
        
    except Exception as e:
        logger.error(f"解析详情页出错 (book_id={book_id}): {e}")
        return None


def get_existing_books() -> Set[Tuple[str, str]]:
    """
    获取数据库中已存在的图书（用于去重）
    
    Returns:
        (书名, 作者) 集合
    """
    existing: Set[Tuple[str, str]] = set()
    try:
        conn = sqlite3.connect(config.BOOK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT bookname, author FROM book")
        for row in cursor.fetchall():
            if row[0] and row[1]:
                existing.add((row[0].strip(), row[1].strip()))
    except Exception as e:
        logger.warning(f"读取现有图书失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return existing


def import_books(book_list: List[BookInfo], skip_duplicate: bool = True) -> Tuple[int, int]:
    """
    导入图书到系统
    
    Args:
        book_list: 图书列表
        skip_duplicate: 是否跳过重复（根据书名+作者判断）
        
    Returns:
        (成功导入数量, 跳过数量)
    """
    imported_count = 0
    skipped_count = 0
    existing = get_existing_books() if skip_duplicate else set()
    
    try:
        conn = sqlite3.connect(config.BOOK_DB_PATH)
        cursor = conn.cursor()
        
        for book in book_list:
            if not book.bookname:
                skipped_count += 1
                continue
            
            # 检查重复
            key = (book.bookname.strip(), book.author.strip())
            if key in existing:
                skipped_count += 1
                logger.info(f"跳过重复图书: {book.bookname}")
                continue
            
            # 插入数据库
            try:
                cursor.execute(
                    """
                    INSERT INTO book (bookname, price, author, pubcom, stock, status) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (book.bookname, book.price, book.author, book.pubcom, book.stock, "在馆")
                )
                imported_count += 1
                existing.add(key)
                logger.info(f"导入图书: {book.bookname}")
            except sqlite3.Error as e:
                skipped_count += 1
                logger.error(f"导入失败 {book.bookname}: {e}")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"导入过程出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    
    logger.info(f"导入完成: 成功 {imported_count} 本, 跳过 {skipped_count} 本")
    return imported_count, skipped_count


def export_to_csv(book_list: List[BookInfo], file_path: Optional[Path] = None) -> Path:
    """
    导出图书数据到CSV
    
    Args:
        book_list: 图书列表
        file_path: 输出文件路径
        
    Returns:
        保存的文件路径
    """
    if file_path is None:
        config.CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_path = config.CSV_OUTPUT_DIR / f"douban_books_export_{timestamp}.csv"
    
    df_data = []
    for book in book_list:
        df_data.append({
            "bookname": book.bookname,
            "author": book.author,
            "price": book.price,
            "pubcom": book.pubcom,
            "stock": book.stock
        })
    
    df = pd.DataFrame(df_data)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    logger.info(f"已导出CSV: {file_path}")
    return file_path


def clear_cache(cache_type: str = "all") -> int:
    """
    清理缓存文件
    
    Args:
        cache_type: 缓存类型 ("list", "detail", "all")
        
    Returns:
        删除的文件数量
    """
    deleted_count = 0
    
    if cache_type in ["list", "all"]:
        if config.LIST_HTML_DIR.exists():
            for f in config.LIST_HTML_DIR.glob("*.html"):
                f.unlink()
                deleted_count += 1
            logger.info(f"清理列表页缓存: {deleted_count} 个")
    
    if cache_type in ["detail", "all"]:
        if config.DETAIL_HTML_DIR.exists():
            for f in config.DETAIL_HTML_DIR.glob("*.html"):
                f.unlink()
                deleted_count += 1
            logger.info(f"清理详情页缓存: {deleted_count} 个")
    
    return deleted_count


class DoubanSpider:
    """
    豆瓣图书爬虫主类
    """
    
    def __init__(self):
        self.config = config
        self.tags: List[Tag] = []
        self.selected_tags: List[Tag] = []
        self.books: List[BookInfo] = []
        self.progress_callback = None
        self._should_stop = False
        
    def load_tags(self, force: bool = False) -> List[Tag]:
        """加载标签列表"""
        self.tags = get_tags(force_download=force)
        return self.tags
    
    def set_selected_tags(self, tag_names: List[str]) -> None:
        """设置选中的标签（通过标签名）"""
        self.selected_tags = [t for t in self.tags if t.name in tag_names]
        logger.info(f"选中标签: {[t.name for t in self.selected_tags]}")
    
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def stop(self):
        """停止爬取"""
        self._should_stop = True
        logger.info("收到停止信号")
    
    def reset(self):
        """重置状态"""
        self._should_stop = False
    
    def _notify_progress(self, message: str, level: str = "info"):
        """通知进度更新"""
        if self.progress_callback:
            try:
                self.progress_callback(message, level)
            except Exception as e:
                logger.error(f"进度回调出错: {e}")
    
    def crawl_tag(self, tag: Tag, page_count: int = 1) -> List[BookInfo]:
        """
        爬取单个标签的图书
        
        Args:
            tag: 标签对象
            page_count: 爬取页数
            
        Returns:
            图书列表
        """
        tag_books: List[BookInfo] = []
        
        for page in range(page_count):
            # 检查是否应该停止
            if self._should_stop:
                self._notify_progress("⏹ 收到停止信号，正在停止...")
                break
            
            start = page * 20  # 豆瓣每页20本
            self._notify_progress(f"📚 正在处理标签: {tag.name}, 第 {page + 1} 页...")
            
            # 下载列表页
            list_file = download_tag_list(tag.url, start=start)
            if list_file is None:
                continue
            
            html_content = load_html_file(list_file)
            if not html_content:
                continue
            
            # 解析图书链接
            book_links = parse_book_links_from_list_html(html_content)
            self._notify_progress(f"   找到 {len(book_links)} 本图书，开始获取详情...")
            
            # 下载详情页并解析
            for idx, link in enumerate(book_links, 1):
                # 再次检查是否应该停止
                if self._should_stop:
                    break
                
                self._notify_progress(f"   [{idx}/{len(book_links)}] 正在获取图书详情...")
                
                detail_file = download_book_detail(link)
                if detail_file is None:
                    continue
                
                # 提取book_id
                book_id = detail_file.stem.split('_')[-1]
                
                detail_html = load_html_file(detail_file)
                if detail_html:
                    book = parse_book_from_detail_html(detail_html, book_id)
                    if book:
                        tag_books.append(book)
                        self._notify_progress(f"   ✅ 已获取: {book.bookname}")
        
        self._notify_progress(f"📖 标签 {tag.name} 爬取完成，共 {len(tag_books)} 本")
        return tag_books
    
    def crawl(self, page_count: int = 1) -> List[BookInfo]:
        """
        爬取所有选中标签的图书
        
        Args:
            page_count: 每个标签爬取页数
            
        Returns:
            总图书列表
        """
        # 重置停止标志
        self._should_stop = False
        
        if not self.selected_tags:
            logger.warning("请先选择要爬取的标签")
            return []
        
        self.books = []
        total_tags = len(self.selected_tags)
        
        for idx, tag in enumerate(self.selected_tags, 1):
            # 检查是否应该停止
            if self._should_stop:
                self._notify_progress("⏹ 爬取已停止")
                break
            
            self._notify_progress(f"📍 进度: [{idx}/{total_tags}] 开始爬取标签: {tag.name}")
            tag_books = self.crawl_tag(tag, page_count=page_count)
            self.books.extend(tag_books)
        
        if not self._should_stop:
            self._notify_progress(f"🎉 全部完成！共爬取 {len(self.books)} 本图书")
        else:
            self._notify_progress(f"⏹ 已停止！共爬取 {len(self.books)} 本图书")
        
        return self.books
    
    def import_to_system(self, skip_duplicate: bool = True) -> Tuple[int, int]:
        """导入到图书管理系统"""
        return import_books(self.books, skip_duplicate=skip_duplicate)
    
    def export_csv(self, file_path: Optional[Path] = None) -> Path:
        """导出为CSV"""
        return export_to_csv(self.books, file_path=file_path)


if __name__ == "__main__":
    # 简单测试
    spider = DoubanSpider()
    tags = spider.load_tags()
    print(f"获取到 {len(tags)} 个标签")
    for i, tag in enumerate(tags[:10]):
        print(f"{i + 1}. {tag.name}")
