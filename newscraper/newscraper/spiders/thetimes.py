from scrapy.spiders import Spider
from scrapy import Request
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class TheTimesSpider(Spider):

    name = "thetimes"
    allowed_domains = [
        "thetimes.co.uk",
    ]
    start_urls = [
        "https://www.thetimes.co.uk/topic/technology?page=1"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse(self, response, **kwargs):
        links = response.xpath("//a[contains(@href, 'https://www.thetimes.co.uk/article')]/@href").extract()
        for link in links:
            yield Request(response.urljoin(link), callback=self.parse_item)

    def parse_item(self, response):
        item = NewsItem()
        pattern = r'\"datePublished\":\"((\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}))'
        datetime_str = response.xpath("//script[@type='application/ld+json']").re_first(pattern)
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj >= (datetime.now() - relativedelta(days=self.days)).date():
                item["url"] = response.url
                title = response.xpath("//h1[@role='heading']/text()").get() or ""
                item["title"] = title.strip()
                summary = response.xpath("//div[@role='heading']/text()").get() or ""
                item["summary"] = summary.strip()
                item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
