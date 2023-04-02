from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class ElDiarioSpider(CrawlSpider):

    name = "eldiario"
    allowed_domains = [
        "eldiario.es",
    ]
    start_urls = [
        "https://www.eldiario.es/tecnologia/"
    ]
    rules = (
        Rule(LinkExtractor(allow="tecnologia"), callback="parse_item"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse(self, response, **kwargs):
        raise CloseSpider("Default parsing method... Closing spider...")

    def parse_item(self, response):
        item = NewsItem()
        datetime_str = response.xpath("//time[@class='date'][1]/@datetime").get()
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj < (datetime.now() - relativedelta(days=self.days)).date():
                raise CloseSpider("No more recent news, closing Spider...")
            item["url"] = response.url
            title = response.xpath("//h1[@class='title']/text()").get() or ""
            item["title"] = title.strip()
            summary = response.xpath("//ul[@class='footer']/li/h2/text()").get() or ""
            item["summary"] = summary.strip()
            item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
