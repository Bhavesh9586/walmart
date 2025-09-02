from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import requests
from lxml import html
import json
from parsel import Selector
import jmespath

app = FastAPI(title="Walmart Scraper API")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


class ScrapeRequest(BaseModel):
    url_or_id: str = Field(..., example="700874136")
    input_type: str = Field(..., example="url")


@app.get("/", response_class=HTMLResponse)
def serve_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def extract_oz(product_name):
    import re
    match = re.search(r'(\d+(\.\d+)?)\s*oz', product_name, re.IGNORECASE)
    if match:
        return match.group(1) + ' oz'
    return 'N/A'


def extract_number(text):
    import re
    match = re.search(r'\d+', text)
    return match.group(0) if match else "N/A"


@app.post("/scrape_Walmart")
def scrape_product(data: ScrapeRequest):
    try:
        url = ""
        if data.input_type == "id":
            if not data.url_or_id.isdigit():
                raise HTTPException(status_code=400, detail="Invalid Product ID. Please enter only numbers.")
            product_id = data.url_or_id
            url = f"https://www.walmart.com/ip/{product_id}"
        elif data.input_type == "url":
            url = data.url_or_id
        else:
            raise HTTPException(status_code=400, detail="Invalid input type selected.")

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'downlink': '3.3',
            'dpr': '1.5',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'cookie': 'ACID=f132cf7b-4589-48ee-8fe8-c966c48df151; _m=9; hasACID=true; userAppVersion=usweb-1.220.0-ada3f07b1e1f576f89fca794606c73b0cd2ce649-8211424r; abqme=true; vtc=V4728pR_oi9F8sQqe2MmrE; _pxhd=2c9a53f76ab083653d9de3f0704f94691fb7195c6f6a9f1cc91bad42f6ff6b98:64a4a479-8260-11f0-b011-bfffa04f1f11; adblocked=false; _pxvid=64a4a479-8260-11f0-b011-bfffa04f1f11; io_id=96c87ff3-4a85-4bb8-b1a4-f79e5f00a3c4; assortmentStoreId=3081; hasLocData=1; AID=wmlspartner=0:reflectorid=0000000000000000000000:lastupd=1756722523690; isoLoc=IN_GJ_t3; pxcts=147dcd3b-87b6-11f0-85e9-36efa8e9ec91; ipSessionTrafficType=External; _xrps=false; ak_bmsc=CCF1651D0BA7756E5F22F1B241518B07~000000000000000000000000000000~YAAQnfQ3F1wo3+qYAQAAEsUiCRxpJ3RryoouvV8yMivoLpNW4+GCJMJ2EuYDXsLV7nN+6kDFtnqPVFvu67xQhspnEPQL8FBsOlsNE9uOflh4ZigfuOui5V5NUjxf4klSo6tPgtNOF6tiNq9FNLyIpO/fKht1mn1lI3Fgapvp4d9BgPAix8Ar/1YgY0100gOS//1UUrN9lEMlDq2f4xJLPby2speUp3gXoAr4wpGJZNe+LVFaQDE0dJVSXqAz7BLZog7AX7rb7iVGDMpH1hiDiLxw7CISzs1Izj+YIT3WSnrm9PtcWWHQn72Li3D2L9KJcy2zGNDRJ1MAI/n4UuZLkL1fcd5pee3zX+nRSjFAEjpe/T0MCKlKgPmHvu8AkweS1YylSD5kGaZLbYkZGg==; _intlbu=false; _shcc=US; auth=MTAyOTYyMDE41Slx9O%2B6QlsXVt91BDEeRioCx9i62DwMR%2BxO4M7IcTEwFJho5Xa05qHWGooOSo6C9oG9yCbmqvBM%2FVX3RE9fBOaaNIDidoJd8SxZyRwsPrpX3ugTOiqZ9UbjwjsFnj62767wuZloTfhm7Wk2KcjyglM949MaUzwsNnQKx2EXSLlnldMBwcojkwIcqaU9ukYHQ1VHqX%2BZ8ow0Sy8w1daX%2FzXL0YWPIvw3DksxF3BuMgoUMk70P8glgOEpLOprhDfMWpzMbgzyqWg6MoSOREDGWnB2Rk3WdSodNJH2AE62Aac7M6G1XakDtff9FPn2JoRInodW2P3eCISS6csdkQedhsRIs81vcrUgkGWg3Nw0%2FJzkoFxX2fgd0wOrdaNao5Nnq%2F%2BuCfbWxBCgJ0vIEH0N6JE5WBBdZBCyKnCQAR7o6eg%3D; bstc=U-mW0Nv5WqUAAKb6PMsCJ8; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xpa=1iMw3|3VCVY|7ZWez|8UWH4|A3LMN|A98YV|ArsR1|E_gpz|FZBtA|H86gh|HTG4X|IRq0V|LCj21|Mx7J7|QPToB|TKwVE|Uquop|V4enY|YQsgA|aj09x|fXtQf|fdm-7|hD1AQ|imMMk|jM1ax|l6fgK|lmqpp|o0JjB|ozs5w|pAaPn|sQbwU|t_PFU|v1QPJ|wJYSP; exp-ck=1iMw317ZWez18UWH41A3LMN1A98YV2ArsR14E_gpz1FZBtA2HTG4XtIRq0V2LCj211Mx7J71QPToB1aj09x1fXtQf1fdm-71hD1AQ1imMMk1l6fgK5lmqpp1ozs5w1sQbwU1t_PFU1; xptwj=uz:3b09f9775c5501edb915:I2SU9ds6QAlep/hRVd0XeH3ceXm2+xokxukvFu7ulgmXNu5F0MAYPllCRu2V0hsMpfMbP70E3FzvGLrgiP4ULkSe193aji3nqZej4RgYMKyBDEyUv7f+xOVjZGQFKd+3PxgarJK+mJ1aaUSrATKO6ZUU8/XHMlV36xBZn/UlB+Rk73eKfCs7oZjgX0Rz52lMyiMb2j8P5g==; bm_mi=80848EDADCCB76768F92A6630F9A3F92~YAAQ5BzFF0muCOCYAQAAp6SNCRyei2SqBd5tUdJslDKOH6qdG6Bu9q8MC4mpHZqJ2cnY1atbrVuZxXY+gIJqNzSxOfIP2x3QdoTsYwRa1JV9PhEAvh2Ze+8WO4qKlLuPxkYovhuD9UVoauW58ss0x9Z8woP7dBfydi1dqE8d9uoLIS8b+FztMq7STEQwLivTWCSQ4Y3giRFXRGI+0YIHHWPOTd8RDQB6Uka8RE0WKAlWxK5TQee8mpSsSlh7HVePSgfrDMMNZZH6r6RmRnk+ZoFRQYapyXrerhxd1AWi94zHfSS6XFq9VedRdsPIYXkuBhnk0A+Yfkdr+zpJkj20OT9AOWhhL/T1mOPWzmPAnVfbQysmvBk/Su++O9as9gq32JpX/cSjs3rOVuX6lHvfQZSvjqWR1AJoeirwDAIdot8AlyjnTtvxlyeAgrk3wJUuz1quVahfyNRnGryZ7qJPw5yhlY5ZDbcqWtzP8fjjJY62EJJVRDfaFzM=~1; xpm=1%2B1756801900%2BV4728pR_oi9F8sQqe2MmrE~%2B0; locDataV3=eyJpc0RlZmF1bHRlZCI6dHJ1ZSwiaXNFeHBsaWNpdCI6ZmFsc2UsImludGVudCI6IlNISVBQSU5HIiwicGlja3VwIjpbeyJub2RlSWQiOiIzMDgxIiwiZGlzcGxheU5hbWUiOiJTYWNyYW1lbnRvIFN1cGVyY2VudGVyIiwiYWRkcmVzcyI6eyJwb3N0YWxDb2RlIjoiOTU4MjkiLCJhZGRyZXNzTGluZTEiOiI4OTE1IEdFUkJFUiBST0FEIiwiY2l0eSI6IlNhY3JhbWVudG8iLCJzdGF0ZSI6IkNBIiwiY291bnRyeSI6IlVTIn0sImdlb1BvaW50Ijp7ImxhdGl0dWRlIjozOC40ODI2NzcsImxvbmdpdHVkZSI6LTEyMS4zNjkwMjZ9LCJzY2hlZHVsZWRFbmFibGVkIjp0cnVlLCJ1blNjaGVkdWxlZEVuYWJsZWQiOnRydWUsInN0b3JlSHJzIjoiMDY6MDAtMjM6MDAiLCJhbGxvd2VkV0lDQWdlbmNpZXMiOlsiQ0EiXSwic3VwcG9ydGVkQWNjZXNzVHlwZXMiOlsiUElDS1VQX1NQRUNJQUxfRVZFTlQiLCJQSUNLVVBfSU5TVE9SRSIsIlBJQ0tVUF9DVVJCU0lERSJdLCJ0aW1lWm9uZSI6IkFtZXJpY2EvTG9zX0FuZ2VsZXMiLCJzdG9yZUJyYW5kRm9ybWF0IjoiV2FsbWFydCBTdXBlcmNlbnRlciIsInNlbGVjdGlvblR5cGUiOiJERUZBVUxURUQifV0sInNoaXBwaW5nQWRkcmVzcyI6eyJsYXRpdHVkZSI6MzguNDc0OCwibG9uZ2l0dWRlIjotMTIxLjM0MzksInBvc3RhbENvZGUiOiI5NTgyOSIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnlDb2RlIjoiVVNBIiwiZ2lmdEFkZHJlc3MiOmZhbHNlLCJ0aW1lWm9uZSI6IkFtZXJpY2EvTG9zX0FuZ2VsZXMiLCJhbGxvd2VkV0lDQWdlbmNpZXMiOlsiQ0EiXX0sImFzc29ydG1lbnQiOnsibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImludGVudCI6IlBJQ0tVUCJ9LCJpbnN0b3JlIjpmYWxzZSwiZGVsaXZlcnkiOnsibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6Ijk1ODI5IiwiYWRkcmVzc0xpbmUxIjoiODkxNSBHRVJCRVIgUk9BRCIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnkiOiJVUyJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzguNDgyNjc3LCJsb25naXR1ZGUiOi0xMjEuMzY5MDI2fSwidHlwZSI6IkRFTElWRVJZIiwic2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsInVuU2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsImFjY2Vzc1BvaW50cyI6W3siYWNjZXNzVHlwZSI6IkRFTElWRVJZX0FERFJFU1MifV0sImlzRXhwcmVzc0RlbGl2ZXJ5T25seSI6ZmFsc2UsImFsbG93ZWRXSUNBZ2VuY2llcyI6WyJDQSJdLCJzdXBwb3J0ZWRBY2Nlc3NUeXBlcyI6WyJERUxJVkVSWV9BRERSRVNTIl0sInRpbWVab25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsInN0b3JlQnJhbmRGb3JtYXQiOiJXYWxtYXJ0IFN1cGVyY2VudGVyIiwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9LCJpc2dlb0ludGxVc2VyIjpmYWxzZSwibXBEZWxTdG9yZUNvdW50IjowLCJyZWZyZXNoQXQiOjE3NTY4MDkyNTMzNDQsInZhbGlkYXRlS2V5IjoicHJvZDp2MjpmMTMyY2Y3Yi00NTg5LTQ4ZWUtOGZlOC1jOTY2YzQ4ZGYxNTEifQ%3D%3D; locGuestData=eyJpbnRlbnQiOiJTSElQUElORyIsImlzRXhwbGljaXQiOmZhbHNlLCJzdG9yZUludGVudCI6IlBJQ0tVUCIsIm1lcmdlRmxhZyI6ZmFsc2UsImlzRGVmYXVsdGVkIjp0cnVlLCJwaWNrdXAiOnsibm9kZUlkIjoiMzA4MSIsInRpbWVzdGFtcCI6MTc1NjcyMjM2Mjc2Mywic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9LCJzaGlwcGluZ0FkZHJlc3MiOnsidGltZXN0YW1wIjoxNzU2NzIyMzYyNzYzLCJ0eXBlIjoicGFydGlhbC1sb2NhdGlvbiIsImdpZnRBZGRyZXNzIjpmYWxzZSwicG9zdGFsQ29kZSI6Ijk1ODI5IiwiZGVsaXZlcnlTdG9yZUxpc3QiOlt7Im5vZGVJZCI6IjMwODEiLCJ0eXBlIjoiREVMSVZFUlkiLCJ0aW1lc3RhbXAiOjE3NTY3MjIzNjI3NjAsImRlbGl2ZXJ5VGllciI6bnVsbCwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCIsInNlbGVjdGlvblNvdXJjZSI6bnVsbH1dLCJjaXR5IjoiU2FjcmFtZW50byIsInN0YXRlIjoiQ0EifSwicG9zdGFsQ29kZSI6eyJ0aW1lc3RhbXAiOjE3NTY3MjIzNjI3NjMsImJhc2UiOiI5NTgyOSJ9LCJtcCI6W10sIm1zcCI6eyJub2RlSWRzIjpbXSwidGltZXN0YW1wIjpudWxsfSwibXBEZWxTdG9yZUNvdW50IjowLCJzaG93TG9jYWxFeHBlcmllbmNlIjpmYWxzZSwic2hvd0xNUEVudHJ5UG9pbnQiOmZhbHNlLCJtcFVuaXF1ZVNlbGxlckNvdW50IjowLCJ2YWxpZGF0ZUtleSI6InByb2Q6djI6ZjEzMmNmN2ItNDU4OS00OGVlLThmZTgtYzk2NmM0OGRmMTUxIn0%3D; _astc=bab225d9d4ad27bb9c270a527bfeefc9; xptc=assortmentStoreId%2B3081~_m%2B9; com.wm.reflector="reflectorid:0000000000000000000000@lastupd:1756801910000@firstcreate:1756722362642"; xptwg=2284864179:131727F122FD220:2EABF25:E5A05E5A:42CAB8DD:D7BD460B:; TS012768cf=01f424e32cf3158f31bf7ec49650a3b76fcb9d573a69e4734b857a4a84c17a259c6d331e0f3f3454bb4f6fb8db0b523e8059bb5a4f; TS01a90220=01f424e32cf3158f31bf7ec49650a3b76fcb9d573a69e4734b857a4a84c17a259c6d331e0f3f3454bb4f6fb8db0b523e8059bb5a4f; TS2a5e0c5c027=08739da77eab2000bb8035bb27e3545f0e53914f615a24af80a5ef64e84dcc618ab4156753f105fb08c28f43b4113000ad8582e30f2b3e80629385b67f4c60def21705cfffbbbf3c45bc0ccc7ac814c3ce7169f02fb7c9995f50dd041fdf541e; akavpau_p2=1756802510~id=a9a649d9154bd7d6bdbcdb6b8a97e50e; _px3=1d9f32fae09e06b33a099ac9ad2567776057f09d7d784270389c722e7baafe74:SUrMWZ0gWy5jp8OqtlcRH/kysoyW3f5Lf4M82B69/2I1QYjTI2TYFkhVqgwcq0+wPHOe2CmIr2VjGBkLQAjeFw==:1000:bzCa9UYDJfJlF2skdL8YyNG/nKfIhEtkndr1n1Xv8kHAg3XcJdezygnrja0N/Q44eYQHmFZ6SDoUOr1DkMDRZjYIFLkKaPNX27aBrFBh9EJNa/slQla5IVA8xOCztkUaeckUaqCebiaVJ3Is2EBG36wSyzY/qYv/1vrr/P8mf0nvNUV+jfPB+PJnkN6UJ2SUo9j0RX1iq+lOmogpFHRmor28dt2mcA/Rq9c+zZYXVfc=; if_id=FMEZARSF4l+8H6GxT2d3fIe2LUUqd4N/PGGqEZg+KcUZjxqU2moiXFokduOQuFytm0dRexP5mGlK5tR1qTduQ6yLHnTWN5HJYc3Wcrv8l9+SvlCN7Yz+adv0jGRCqwRaz4kf4LJgCf91nxSKDTXYtnyqnyQ2NLWO9B6RKCdhWNxb0U3DTw3yacfuYEUokEbKpgD2p87mQiyv2e1iq1Xeo8vm1A9kBK6Jm3/DV0oTOyE+agWhSzTmf9WC+A2eRbDLu/Yz5fPquOw3bTkgqIlcP5X8gVLL905ezlQM3oE6SuKZnVEjkcB01i6WmVxflFSA1pxEg6U0aS5+vXXPGnJx15rGP3D2; TS016ef4c8=017cd48893b56d48158624bd55406018c9295e9c0398ea64616087404d5707406be608c3ca327422a37d5712c325cbf5e84c50c50c; TS01f89308=017cd48893b56d48158624bd55406018c9295e9c0398ea64616087404d5707406be608c3ca327422a37d5712c325cbf5e84c50c50c; TS8cb5a80e027=084c268966ab200010c2ae349a064fcf61f5b56e32d10fd9db3c52ae9cc8580325db2a26857c3f24088229da961130008eab49b69800ebd94c2e9916d54e56aac3e1e43a790005c9792f10378f5c2b257d02c50d1ea3148bf6860da69f277c6c; bm_sv=30F65099A657147DBADCE2248C33F55E~YAAQ7xzFF8QFheuYAQAA182NCRxmKoRyOEC52ncDo/H/IwjtT6Me4/p5cHdV8wRwsD9NQOIGF4WqSOduRkIa1XxTvsKIVEX9msbqqKcBCOnd3vlggh3Ew0whEnEpl9zsISzoDhp6cSrg8Lfj6qAzfuumna6WGozZPLvjf/g8hXOEnWwG6ZB5jh6YaKyzmwy/2SIfIIbRunt5wTccf1U7RfEUixQDGWtSjlL+dQuqaMi/qQ//F88+UjvbW1a/OG8O3Qw=~1; _pxde=eacdb50a61757b918c930c0a71f38060ed90fa33c58ad0dc6d68953827705ea7:eyJ0aW1lc3RhbXAiOjE3NTY4MDE5MTMyMTh9',
        }

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=500,
                                detail=f"Failed to fetch product page. Status code: {response.status_code}")

        selector = Selector(response.text)
        # Dentro de la función scrape_product, después de definir el 'selector'
        shop_confidently = selector.xpath(
            '//div[@class="flex items-center"]/span[@class="dib nowrap overflow-hidden f5 ph2"]/text()').getall()

        script_data = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        data_json = json.loads(script_data)
        reviews_data = []
        if not script_data:
            raise HTTPException(status_code=500, detail="Unable to extract product data (missing script).")
        customer_reviews = jmespath.search(
            'props.pageProps.initialData.data.reviews.customerReviews',
            data_json
        )
        if customer_reviews:
            for review in customer_reviews:
                reviews_data.append({
                    "user": review.get("userNickname"),
                    "title": review.get("reviewTitle"),
                    "text": review.get("reviewText"),
                    "rating": review.get("rating")
                })
        product_data = jmespath.search("props.pageProps.initialData.data", data_json)

        if not product_data:
            raise HTTPException(status_code=500, detail="Product data structure not found.")

        # Extract fields from JSON
        title = jmespath.search("product.name", product_data)
        brand = jmespath.search("product.brand", product_data)
        price = jmespath.search("product.priceInfo.currentPrice.price", product_data)
        upc = jmespath.search("product.upc", product_data)
        product_url = "https://www.walmart.com" + jmespath.search(
            "contentLayout.pageMetadata.pageContext.itemContext.productUrl", product_data
        )
        main_images = jmespath.search("product.imageInfo.allImages[*].url", product_data) or []
        description_html = jmespath.search("product.shortDescription", product_data)
        description = " ".join(Selector(description_html).xpath("//text()").getall()).strip() if description_html else None
        long_description_html = jmespath.search("idml.longDescription", product_data)
        description_full = " ".join(Selector(long_description_html).xpath("//text()").getall()).strip() if long_description_html else None
        nutrition = jmespath.search("idml.nutritionFacts", product_data)
        ingredients = jmespath.search("idml.ingredients.ingredients.value", product_data)
        location = jmespath.search("contentLayout.pageMetadata.location", product_data) or {}
        location_info = f"{location.get('city', '')}, {location.get('stateOrProvinceCode', '')}, {location.get('postalCode', '')}".strip(', ')
        state = location.get("stateOrProvinceCode")

        specifications = jmespath.search("idml.specifications", product_data) or []
        allergens = next((s.get("value") for s in specifications if s.get("name") == "Food Allergen Statements"), "N/A")
        calories = next((s.get("value") for s in specifications if s.get("name") == "Calories Per Serving"), "N/A")
        calories = extract_number(calories)

        highlights = jmespath.search("idml.productHighlights", product_data) or []
        pack_size = next((h.get("value") for h in highlights if h.get("name") == "Count "), "1")

        return {
            "upc": upc,
            "brand": brand,
            "title": title,
            "url": product_url,
            "main_image": main_images[0] if main_images else None,
            "all_images": main_images,
            "description": description,
            "description_full": description_full,
            "price": price,
            "net_weight": extract_oz(title) if title else 'N/A',
            "pack_size": pack_size,
            "allergens": allergens,
            "calories": calories,
            "state": state,
            "location_info": location_info,
            "nutrition": nutrition,
            "ingredients": ingredients,
            "reviews":reviews_data,
            "shop_confidently": shop_confidently
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
