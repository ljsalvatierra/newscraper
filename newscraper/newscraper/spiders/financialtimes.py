from scrapy.spiders import Spider
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class FinancialTimesSpider(Spider):

    name = "financialtimes"
    allowed_domains = [
        "ft.com",
    ]
    start_urls = [
        "https://www.ft.com/technology"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse_node(self, node):
        link = node.xpath(".//div[@class='o-teaser__heading']/a/@href").get()
        title = node.xpath(".//div[@class='o-teaser__heading']/a/text()").get() or ""
        summary = node.xpath(".//p[@class='o-teaser__standfirst']/a/text()").get() or ""
        return link, title, summary

    def parse(self, response, **kwargs):
        datetime_str = response.xpath("//meta[@property='publishedDate']/@content").get()
        parent_xpaths = [
            "//div[contains(@class, 'o-teaser--top-story')]//div[@class='o-teaser__content']",  # Top story
            "//div[@data-trackable='top-stories-column-one']//div[@class='o-teaser__content']",  # News
            "//div[@class='css-grid__item-bottom']//ul"
            "/li[contains(@class, 'o-teaser-collection__item')]"
            "//div[@class='o-teaser__content']",  # More News
        ]
        for xpath in parent_xpaths:
            for node in response.xpath(xpath):
                link, title, summary = self.parse_node(node)
                url = response.urljoin(link)
                yield self.parse_item(url=url, title=title, summary=summary, datetime_str=datetime_str)

    def parse_item(self, **kwargs):
        item = NewsItem()
        datetime_str = kwargs.get("datetime_str", None)
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj >= (datetime.now() - relativedelta(days=self.days)).date():
                item["url"] = kwargs.get("url", None)
                item["title"] = kwargs.get("title", "").strip()
                item["summary"] = kwargs.get("summary", "").strip()
                item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
