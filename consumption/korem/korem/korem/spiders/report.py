import scrapy
from scrapy_splash import SplashRequest
import os
from pathlib import Path


class ReportSpider(scrapy.Spider):
    name = "report"
    allowed_domains = ["www.korem.kz"]
    parent_path = Path(os.path.abspath(__file__)).parents[4]
    data_path = 'dataset\consumption_data'
    full_path = os.path.join(parent_path, data_path)

    script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(2))
            return {
                html = splash:html(),
            }
            end
    '''
    start_urls = [f'https://www.korem.kz/rus/analitika/otchety_za_mesyac/?cid=0&page={i}' for i in range(1,16)]
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.parse, endpoint='execute', args={
                'lua_source': self.script
            })

    def parse(self, response):
        items = response.css('div.list a.item')
        for item in items:
            title = item.css('div.title ::text').get()
            link = response.urljoin(item.css('::attr(href)').get())
            yield {
                'Title': title,
                'file_urls': [link] 
            }

   

