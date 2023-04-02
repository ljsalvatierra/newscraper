from scrapy.spiders import Spider
from scrapy import Request
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class CNNSpider(Spider):

    name = "cnn"
    allowed_domains = [
        "cnn.com",
    ]
    start_urls = [
        "https://edition.cnn.com/business/tech"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse(self, response, **kwargs):
        links = response.xpath("//a[contains(@class, 'container__link')]/@href").extract()
        for link in links:
            yield Request(response.urljoin(link), callback=self.parse_item)

    def parse_item(self, response):
        item = NewsItem()
        datetime_str = response.xpath("//meta[@property='article:published_time']/@content").get()
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj >= (datetime.now() - relativedelta(days=self.days)).date():
                item["url"] = response.url
                title = response.xpath("//h1[@id='maincontent']/text()").get() or ""
                item["title"] = title.strip()
                summary = response.xpath("//div[contains(@class, 'article__content')]/p[1]/text()").get() or ""
                if not summary:
                    summary = response.xpath("//div[@data-editable='description']/text()").get() or ""
                item["summary"] = summary.strip()
                item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
