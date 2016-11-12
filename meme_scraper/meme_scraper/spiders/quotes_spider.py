import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.NUM_PAGES = 1
        self.resolution = "500x500"

    def start_requests(self):
        urls = [
            'https://memegenerator.net/memes/popular/alltime',
        ]
        for i in range(2, 1+self.NUM_PAGES):
            print("page!", i)
            urls.append('https://memegenerator.net/memes/popular/alltime/page/%d' % i)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div.item_medium_small'):
            yield {
                'base_url': quote.css('a::attr(href)').extract_first(),
                'base_image': quote.css('a img::attr(src)').extract_first(),
            }
            base_url = quote.css('a::attr(href)').extract_first()
            if base_url is not None:
                full_base_url = response.urljoin(base_url)
                request = scrapy.Request(full_base_url, callback=self.parse_meme_page)
                request.meta['base_url'] = base_url
                yield request

    def parse_meme_page(self, response):
        meme_name = ""
        for header in response.css('h1'):
            meme_name = header.css('h1::text').extract_first()
            break

        for meme_entry in response.css('div.item_medium_small'):
            text = meme_entry.css('a img::attr(alt)').extract_first()
            # text = text[3+len(meme_name):]
            yield {
                'base_url': response.meta['base_url'],
                'text': text,
                'meme_url': meme_entry.css('a img::attr(src)').extract_first(),
            }

        pager = response.css('div.pager ul.pager')
        entries = [entry for entry in pager.css('ul li')]
        next_url = entries[-1].css('a::attr(href)').extract_first()
        if next_url is not None:
            full_next_url = response.urljoin(next_url)
            request = scrapy.Request(full_next_url, callback=self.parse_meme_page)
            request.meta['base_url'] = response.meta['base_url']
            yield request


    # def parse(self, response):
    #     page = response.url.split("/")[-2]
    #     filename = 'quotes-%s.html' % page
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)
    #     self.log('Saved file %s' % filename)