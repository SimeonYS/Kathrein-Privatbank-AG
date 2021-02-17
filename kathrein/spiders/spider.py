import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import KathreinItem
pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.kathrein.at/de/?+News-Kathrein-News+&id=2500,,1000136/',
                  'https://www.kathrein.at/de/?+Presseaussendungen-Kathrein-Presseaussendungen+&id=2500,,1000138']

    def parse(self, response):
        articles = response.xpath('//ul[@class="article-links content first"]/li')

        for article in articles:
            date = article.xpath('.//span[@class="date list-date"]//text()').get().strip()
            links = article.xpath('.//a[@class="list-summary"]/@href').get()
            url = response.urljoin(links)
            yield response.follow(url, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        item = ItemLoader(KathreinItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//text()').get()
        content = response.xpath('//div[@class="content-container style999"]//text()').getall()
        content = [text.strip() for text in content if text.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()