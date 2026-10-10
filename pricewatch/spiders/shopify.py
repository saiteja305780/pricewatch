import scrapy

PAGE_SIZE = 250

class ShopifySpider(scrapy.Spider):
    name = "shopify"

    def __init__(self, store=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not store:
            raise ValueError("Usage: scrapy crawl shopify -a store=https://example.com")
        self.store = store.rstrip("/")
        self.start_urls = [self._page_url(1)]

    def _page_url(self, page):
        return f"{self.store}/products.json?limit={PAGE_SIZE}&page={page}"

    def parse(self, response, page=1):
        products = response.json().get("products", [])
        for p in products:
            for v in p.get("variants", []):
                title = p["title"]
                if v.get("title") and v["title"] != "Default Title":
                    title = f"{title} - {v['title']}"
                yield {
                    "store": self.store.replace("https://", "").replace("http://", "").replace("www.", ""),
                    "variant_id": v["id"],
                    "url": f"{self.store}/products/{p['handle']}?variant={v['id']}",
                    "title": title,
                    "vendor": p.get("vendor", ""),
                    "category": p.get("product_type") or "uncategorized",
                    "price": v.get("price"),
                    "compare_at_price": v.get("compare_at_price"),
                    "in_stock": bool(v.get("available")),
                }

        if len(products) == PAGE_SIZE:
            yield scrapy.Request(self._page_url(page + 1),
                                 callback=self.parse, cb_kwargs={"page": page + 1})