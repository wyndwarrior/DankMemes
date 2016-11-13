import scrapy

def is_gif(url):
    return url[-4:] == '.gif' or url[-5:] == '.gifv'

def is_image(url):
    return url[-4:] == '.jpg' or url[-5:] == '.jpeg' or url[-4:] == '.png'

class MemesSpider(scrapy.Spider):
    name = "memes"

    def __init__(self):
        self.NUM_PAGES = 1
        self.resolution = "500x500"

    def start_requests(self):
        reddit_url = 'https://www.reddit.com/'
        subreddits = [
            'r/dankmemes/',
            'r/memes/',
            'r/funny/',
            'r/harambe/',
        ]

        for subreddit in subreddits:
            for page_type in ['top/', 'top/?sort=top&t=all']:
                request = scrapy.Request(url=reddit_url+subreddit, callback=self.parse_reddit)
                request.meta['subreddit'] = subreddit
                yield request

    def parse_reddit(self, response):
        for post in response.css('div.sitetable div.thing'):
            likes = post.css('div.unvoted::text').extract_first()
            meme_url = post.css('a::attr(href)').extract_first()
            title = post.css('a::text').extract_first()

            # skip comments (TODO)
            if meme_url.lower().find(response.meta['subreddit']) >= 0:
                continue

            # skip gifs
            if is_gif(meme_url):
                continue

            if meme_url.find('imgur') >= 0 and not is_image(meme_url):
                meme_url += '.jpg'      # code alert!

            yield {
                'likes': likes,
                'meme_url': meme_url,
                'title': title,
                'subreddit': response.meta['subreddit']
            }
        next_page = response.css('span.next-button a::attr(href)').extract_first()
        try:
            request = scrapy.Request(next_page, callback=self.parse_reddit)
            request.meta['subreddit'] = response.meta['subreddit']
            yield request
        except TypeError:
            pass

    def parse_meme_generator(self, response):
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
            delimiter_index = text.find('-')
            if delimiter_index >= 0:
                text = text[delimiter_index:]
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