import logging
from scrapy.exceptions import DropItem
from pydantic import ValidationError
from sqlalchemy import select, desc
from .models import ProductItem
from .db import Session, Product, PricePoint, ScrapeRun, init_db, now

log = logging.getLogger(__name__)

class ValidationPipeline:
    def process_item(self, item):
        try:
            return ProductItem(**item).model_dump()
        except ValidationError as e:
            raise DropItem(f"Invalid item {item.get('variant_id')}: {e}")

class SQLitePipeline:
    def open_spider(self):
        init_db()
        self.new = self.changed = self.unchanged = 0
        self.store = None
        self.run_id = None

    def process_item(self, item):
        if self.run_id is None:
            self.store = item["store"]
            with Session.begin() as s:
                run = ScrapeRun(store=self.store)
                s.add(run)
                s.flush()
                self.run_id = run.id

        with Session.begin() as s:
            product = s.scalar(select(Product).where(
                Product.store == item["store"],
                Product.variant_id == item["variant_id"]))
            if product is None:
                product = Product(store=item["store"], variant_id=item["variant_id"],
                                  url=item["url"], title=item["title"],
                                  vendor=item["vendor"], category=item["category"])
                s.add(product)
                s.flush()
                self.new += 1
                s.add(PricePoint(product_id=product.id, price=item["price"],
                                 compare_at_price=item["compare_at_price"],
                                 in_stock=item["in_stock"]))
                return item

            last = s.scalar(select(PricePoint)
                            .where(PricePoint.product_id == product.id)
                            .order_by(desc(PricePoint.scraped_at), desc(PricePoint.id)).limit(1))
            if (last is None or last.price != item["price"]
                    or last.in_stock != item["in_stock"]
                    or last.compare_at_price != item["compare_at_price"]):
                s.add(PricePoint(product_id=product.id, price=item["price"],
                                 compare_at_price=item["compare_at_price"],
                                 in_stock=item["in_stock"]))
                self.changed += 1
            else:
                self.unchanged += 1
        return item

    def close_spider(self):
        if self.run_id is not None:
            with Session.begin() as s:
                run = s.get(ScrapeRun, self.run_id)
                run.finished_at = now()
                run.new_count = self.new
                run.changed_count = self.changed
                run.unchanged_count = self.unchanged
        log.info(f"New: {self.new} | Changed: {self.changed} | Unchanged: {self.unchanged}")