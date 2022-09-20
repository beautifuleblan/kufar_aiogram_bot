from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio

async def parse_data(url: str):
    async with ClientSession() as session:
        request = await session.get(url)
        soup = BeautifulSoup(await request.read(), 'html.parser')
        cards = soup.find(class_="styles_cards__PXCps").find_all('section')
        if cards:
            for card in cards:
                vip = card.find(class_="styles_container__FQ2Zf").find('object')
                if not vip:
                    name = card.find(class_="styles_title__wj__Y").text.strip()
                    price = card.find(class_="styles_price__x_wGw").text.strip()
                    link = card.find(class_="styles_wrapper__pb4qU").get('href')
                    return name, price, link



if __name__ == '__main__':
    url = 'https://www.kufar.by/l/telefony-i-planshety'
    asyncio.run(parse_data(url))
