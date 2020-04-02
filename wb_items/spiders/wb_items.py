import time

import scrapy


class WbSpider(scrapy.Spider):
    name = 'wb'
    allowed_domains = ['wildberries.ru']
    start_urls = [
        # 'https://www.wildberries.ru/catalog/obuv/zhenskaya/sabo-i-myuli/myuli',
        'https://www.wildberries.ru/catalog/dlya-doma/postelnye-prinadlezhnosti/matrasy-dlya-krovati',
    ]

    def parse(self, response):
        # items_links = response.xpath('//a[@class="ref_goods_n_p"]')
        # yield from response.follow_all(items_links, self.parse_items)
        for href in response.xpath('//a[@class="ref_goods_n_p"]/@href'):
            yield response.follow(href, self.parse_items)

        # pagination_links = response.xpath('//a[@class="next"]')
        # yield from response.follow_all(pagination_links, self.parse)
        for href in response.xpath('//a[@class="next"]/@href'):
            yield response.follow(href, self.parse)

    def parse_items(self, response):
        in_stock = response.xpath(
            '//button[contains(@class, "j-add-to-card")]/@class').get()

        current = response.xpath(
            '//div[@class="discount-tooltipster-content"]/p[2]/span[2]/text()').get()
        original = response.xpath(
            '//span[@class="old-price"]/del/text()').get()
        if not current:
            current = original
        if current and original:
            current = float(current.replace(u'\xa0', '').replace('₽', ''))
            original = float(original.replace(u'\xa0', '').replace('₽', ''))

        view360 = []
        view360_url = response.xpath(
            '//div[@id="container_3d"]/@data-path').get()
        if view360_url:
            for i in range(12):
                view360 += [f'{view360_url}/{i}.jpg']

        info = response.xpath('//div[@class="card-add-info"]')
        metadata = {
            '__description': response.xpath('//meta[@property="og:description"]/@content').get(),
            'АРТИКУЛ': response.xpath('//div[@class="article"]/span/text()').get()
        }
        consist = response.xpath('//h1[@class="title"]/text()').get()
        if consist:
            metadata[consist.strip().upper()] = info.xpath(
                'div[@class="i-composition-v1 j-collapsable-composition i-collapsable-v1"]/span/text()').get()
        for param in info.xpath('//div[@class="pp"]'):
            metadata[param.xpath('span[1]/b/text()').get().upper()
                     ] = param.xpath('span[2]/text()').get()

        yield {
            'timestamp': int(time.time()),
            'RPC': response.xpath('//div[@class="article"]/span/text()').get(),
            'url': response.xpath('//meta[@property="og:url"]/@content').get(),
            'title': response.xpath('//meta[@property="og:title"]/@content').get(),
            'marketing_tags': response.css('li.tags-group-item > a::text').getall(),
            'brand': response.xpath('//a[@id="brandBannerImgRef"]/@title').get(),
            'section': response.xpath('//a[@class="breadcrumbs_url"]/span/text()').getall(),
            'price_data': {
                'current': current,
                'original': original,
                'sale_tag': response.xpath('//div[@class="discount-tooltipster-content"]/p[2]/span[1]/text()').get()
            },
            'stock': {
                'in_stock': False if 'hide' in in_stock else True,
                # 'count': ''
            },
            'assets': {
                'main_image': response.xpath('//div[@id="photo"]/a/img/@src').get(),
                'set_images': response.xpath('//ul[@class="carousel"]/li/a/@rev').getall(),
                'view360': view360,
                'video': response.xpath('//meta[@property="og:video"]/@content').getall()
            },
            'metadata': metadata
        }
