# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, get_app
import sqlite3
from enum import Enum
from datetime import datetime, timedelta

from scrapy.exceptions import DropItem

from newscraper.items import DATE_FORMAT

from settings.firestore import CERT_FILENAME, CLEANUP_DAYS, BATCH_LIMIT


class News(Enum):
    url = "url"
    title = "title"
    summary = "summary"
    like = "like"
    published = "published"


class CloudFirestoreNewsPipeline:

    def __init__(self):
        script_parent_path = os.path.dirname(os.path.abspath(__file__))
        cert_filename = CERT_FILENAME
        cert_abspath = os.path.join(os.path.dirname(script_parent_path), cert_filename)
        cred = credentials.Certificate(cert_abspath)
        try:
            app = get_app()
        except ValueError:
            app = firebase_admin.initialize_app(cred)
        self.app = app
        self.db = firestore.client()
        self.collection = self.db.collection("newscraper")

    def exists(self, item, spider):
        documents = self.collection.where(News.url.value, "==", item[News.url.value]).get()
        if documents:
            spider.logger.warn("Item already in database: %s" % item[News.url.value])
            return True
        else:
            return False

    def save_item(self, item, spider):
        if not self.exists(item, spider):
            published = datetime.strptime(item[News.published.value], DATE_FORMAT)
            new_document = self.collection.document()
            new_document.set({
                News.url.value: item[News.url.value],
                News.title.value: item[News.title.value],
                News.summary.value: item[News.summary.value],
                News.published.value: published,
                News.like.value: False,
            })

    def missing_fields(self, item, spider):
        url = item.get(News.url.value, False)
        title = item.get(News.title.value, False)
        summary = item.get(News.summary.value, False)
        published = item.get(News.published.value, False)
        missing = []
        if not url:
            spider.logger.warn("Item missing URL")
            missing.append("URL")
        if not title:
            spider.logger.warn("Item missing Title")
            missing.append("Title")
        if not summary:
            spider.logger.warn("Item missing Summary")
            missing.append("Summary")
        if not published:
            spider.logger.warn("Item missing Published")
            missing.append("Published")
        return missing

    def process_item(self, item, spider):
        missing = self.missing_fields(item, spider)
        if missing:
            raise DropItem("Missing required fields {}".format(", ".join(missing)))
        else:
            self.save_item(item, spider)
            return item

    def cleanup(self):
        batch = self.db.batch()
        now = datetime.utcnow()
        cutoff = now - timedelta(days=CLEANUP_DAYS)
        query = self.collection.where('published', '<', cutoff)
        for doc in query.stream():
            batch.delete(doc.reference)
        batch.commit()

    def remove_all_documents(self):
        docs_processed = 0
        batch = self.db.batch()
        for doc in self.collection.get():
            batch.delete(doc.reference)
            docs_processed += 1
            if docs_processed % BATCH_LIMIT == 0:
                batch.commit()
                batch = self.db.batch()
        # Commit any remaining changes
        if docs_processed % BATCH_LIMIT != 0:
            batch.commit()


class SqliteNewsPipeline:

    def __init__(self):
        self.con = sqlite3.connect("sqlite.db")
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS newscraper(
            id integer PRIMARY KEY,
            url text NOT NULL,
            title text NOT NULL,
            summary text NOT NULL,
            date text NOT NULL
        )
        """)

    def exists(self, item, spider):
        self.cur.execute("select * from newscraper where url = ?", (item["url"],))
        result = self.cur.fetchone()
        if result:
            spider.logger.warn("Item already in database: %s" % item["url"])
            return True
        else:
            return False

    def save_item(self, item, spider):
        if not self.exists(item, spider):
            self.cur.execute("""
                INSERT INTO newscraper (url, title, summary, date) VALUES (?, ?, ?, ?)
            """, (
                item["url"],
                item["title"],
                item["summary"],
                item["date"],
            ))
            self.con.commit()

    def missing_fields(self, item, spider):
        url = item.get("url", False)
        title = item.get("title", False)
        summary = item.get("summary", False)
        date = item.get("date", False)
        missing = []
        if not url:
            spider.logger.warn("Item missing URL")
            missing.append("URL")
        if not title:
            spider.logger.warn("Item missing Title")
            missing.append("Title")
        if not summary:
            spider.logger.warn("Item missing Summary")
            missing.append("Summary")
        if not date:
            spider.logger.warn("Item missing Date")
            missing.append("Date")
        return missing

    def process_item(self, item, spider):
        missing = self.missing_fields(item, spider)
        if missing:
            raise DropItem("Missing required fields {}".format(", ".join(missing)))
        else:
            self.save_item(item, spider)
            return item
