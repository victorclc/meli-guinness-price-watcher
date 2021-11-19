import os
from typing import Optional, List

import requests

SEARCH_ENDPOINT = "https://api.mercadolibre.com/sites/MLB/search?q="
PRICE_THRESHOLD = 14.00
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")


def search(product_name: str, filter_out: Optional[List[str]] = None):
    url = SEARCH_ENDPOINT + product_name
    response = requests.get(url).json()
    if filter_out:
        return list(
            filter(
                lambda i: not any(f in i["title"] for f in filter_out),
                response["results"],
            )
        )
    return response["results"]


def notify(seller_id: str, link: str, price: float):
    payload = {
        "embeds": [
            {
                "title": f"GUINNESS BARATA",
                "description": "",
                "color": 0xFFE203,
                "fields": [
                    {"name": "Vendedor", "value": str(seller_id), "inline": False},
                    {"name": "Preço", "value": str(price), "inline": False},
                    {"name": "Link", "value": link, "inline": False},
                ],
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=payload)


def guinness_watcher_handler(event, context):
    meli_results = search("Guinness", ["Copo", "Kit"])
    cheap_guinnesses = filter(lambda mr: mr["price"] < PRICE_THRESHOLD, meli_results)

    for cheap_guinness in cheap_guinnesses:
        seller_id = cheap_guinness["official_store_id"]
        link = cheap_guinness["permalink"]
        price = cheap_guinness["price"]
        notify(seller_id, link, price)
