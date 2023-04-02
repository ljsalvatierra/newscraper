from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    for spider_name in process.spider_loader.list():
        process.crawl(spider_name, days=2)
    process.start()
