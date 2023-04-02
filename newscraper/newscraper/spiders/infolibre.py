from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class InfolibreSpider(CrawlSpider):

    name = "infolibre"
    allowed_domains = [
        "infolibre.es",
    ]
    start_urls = [
        "https://www.infolibre.es/medios/"
    ]
    rules = (
        Rule(LinkExtractor(allow="medios"), callback="parse_item"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse(self, response, **kwargs):
        raise CloseSpider("Default parsing method... Closing spider...")

    def parse_item(self, response):
        item = NewsItem()
        pattern = r'\"datePublished\":\"((\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}))'
        datetime_str = response.xpath("//script[@type='application/ld+json']").re_first(pattern)
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj < (datetime.now() - relativedelta(days=self.days)).date():
                raise CloseSpider("No more recent news, closing Spider...")
            item["url"] = response.url
            title = response.xpath("//h1[@class='title']/text()").get() or ""
            item["title"] = title and title.strip() or ""
            summary1 = response.xpath("//ul[@class='footer']/li[1]/text()[2]").get() or ""
            summary2 = response.xpath("//ul[@class='footer']/li[2]/text()[2]").get() or ""
            summary = ". ".join([summary1, summary2])
            item["summary"] = summary.strip()
            item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
