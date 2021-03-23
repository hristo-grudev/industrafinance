import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import IndustrafinanceItem
from itemloaders.processors import TakeFirst
import requests

url = "https://industra.finance/banka/jaunumi"

base_payload = "act=loadNews&p={}&f=%23page%3D2&all=0"
headers = {
  'authority': 'industra.finance',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://industra.finance',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://industra.finance/banka/jaunumi',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': 'sid=k2jljbmp2l4qk3l63aa6evbc9e; _fbp=fb.1.1616420559635.910189242; _ga=GA1.2.232028494.1616420560; _gid=GA1.2.575768357.1616420560; _gat_gtag_UA_55180755_1=1; new_cookieconsent_status=allow'
}


class IndustrafinanceSpider(scrapy.Spider):
	name = 'industrafinance'
	start_urls = ['https://industra.finance/banka/jaunumi#page=9999']
	page = 1

	def parse(self, response):
		payload = base_payload.format(self.page)
		data = requests.request("POST", url, headers=headers, data=payload)
		data_dict = json.loads(data.text)
		raw_data = scrapy.Selector(text=data_dict['html'])
		post_links = raw_data.xpath('//div[@class="news-inner-block"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if post_links:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="article-content text-content with-intro-text"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="header-attr"]/time/text()').get()

		item = ItemLoader(item=IndustrafinanceItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
