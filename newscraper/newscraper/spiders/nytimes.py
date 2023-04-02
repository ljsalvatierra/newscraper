from scrapy.spiders import Spider
from datetime import datetime
from dateutil.relativedelta import relativedelta

from newscraper.items import NewsItem, DATE_FORMAT
from newscraper.libs.utils.date import get_date_from_str
from newscraper.libs.conf import RELATIVEDELTA_DAYS


class NYTimesSpider(Spider):

    name = "nytimes"
    allowed_domains = [
        "nytimes.com",
    ]
    start_urls = [
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = kwargs.get("days", RELATIVEDELTA_DAYS)

    def parse(self, response, **kwargs):
        posts = response.xpath("//channel/item")
        for post in posts:
            yield self.parse_item(post)

    def parse_item(self, post):
        item = NewsItem()
        datetime_str = post.xpath('pubDate/text()').get()
        if datetime_str and isinstance(datetime_str, str):
            date_obj = get_date_from_str(datetime_str)
            if date_obj >= (datetime.now() - relativedelta(days=self.days)).date():
                item["url"] = post.xpath('link/text()').get()
                title = post.xpath('title/text()').get() or ""
                item["title"] = title.strip()
                summary = post.xpath('description/text()').get() or ""
                item["summary"] = summary.strip()
                item["published"] = date_obj.strftime(DATE_FORMAT)
        return item
