import asyncio
import random
from playwright.async_api import async_playwright
import json
import csv
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import os


async def fetch_room_data(page_url, api_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        room_data = []

        async def handle_response(response):
            if api_url in response.url and response.status == 200:
                try:
                    json_data = await response.json()
                    room_data.append(json_data)
                    print(f"Captured data: {json_data}")
                except Exception as e:
                    print(f"Error decoding JSON: {e}")

        page.on("response", handle_response)

        try:
            await page.goto(page_url, wait_until='networkidle', timeout=60000)

            await page.mouse.move(random.randint(100, 200), random.randint(100, 200))
            await page.wait_for_timeout(random.randint(1000, 3000))
            await page.click('body')

            await asyncio.sleep(10)

        except Exception as e:
            print(f"Error occurred while loading the page: {e}")
        finally:
            await browser.close()

        return room_data[0] if room_data else None


def extract_url_params(url):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    hotels_id = parsed_url.path.split('/')[-1]
    check_in = params.get('checkIn', [''])[0]
    check_out = params.get('checkOut', [''])[0]
    return hotels_id, check_in, check_out


def extract_and_save_data(data):
    rates = []
    if data and 'roomTypes' in data:
        for room_type in data['roomTypes']:
            room_name = room_type.get('name', 'N/A')
            max_occupancy = room_type.get('maxOccupantCount', 'N/A')
            for offer in room_type.get('offers', []):
                rate_info = {
                    "Room_name": room_name,
                    "Rate_name": offer.get('description', 'N/A'),
                    "Number_of_Guests": max_occupancy,
                    "Cancellation_Policy": offer.get('cancellationPolicy', {}).get('description', 'N/A'),
                    "Price": offer.get('charges', {}).get('payableAtBooking', {}).get('total', {}).get('amount', 'N/A'),
                    "Currency": offer.get('charges', {}).get('payableAtBooking', {}).get('total', {}).get('currency',
                                                                                                          'N/A'),
                    "Top_Deal": offer.get('isTopDeal', False)
                }
                rates.append(rate_info)

    with open('rates.json', 'w', encoding='utf-8') as file:
        json.dump(rates, file, ensure_ascii=False, indent=4)

    print("Data saved to rates.json")


def generate_checkin_checkout_dates(hotels_id, check_in, num_combinations):
    dates = []
    base_date = datetime.strptime(check_in, '%Y-%m-%d')
    for i in range(num_combinations):
        check_in_date = base_date + timedelta(days=i)
        check_out_date = check_in_date + timedelta(days=1)
        dates.append({
            "hotels_id": hotels_id,
            "check-in": check_in_date.strftime('%Y-%m-%d'),
            "check-out": check_out_date.strftime('%Y-%m-%d')
        })
    return dates


def save_to_csv(data, filename):
    if not data:
        print(f"No data to save to {filename}")
        return

    keys = data[0].keys()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"Data saved to {filename}")


async def main():
    # url and api for Strand Palace Hotel, London
    page_url = "https://www.qantas.com/hotels/properties/19443?adults=2&checkIn=2024-06-21&checkOut=2024-06-22&children=0&infants=0&location=London%2C%20England%2C%20United%20Kingdom&page=1&payWith=cash&searchType=list&sortBy=popularity"
    api_url = "https://www.qantas.com/hotels/api/ui/properties/19443/availability?checkIn=2024-06-21&checkOut=2024-06-22&adults=2&children=0&infants=0&payWith=cash"

    # url and api for The Tower Hotel, London
    # page_url = 'https://www.qantas.com/hotels/properties/181129?adults=2&checkIn=2024-06-21&checkOut=2024-06-22&children=0&infants=0&location=London%2C%20England%2C%20United%20Kingdom&page=1&payWith=cash&searchType=list&sortBy=popularity'
    # api_url = 'https://www.qantas.com/hotels/api/ui/properties/181129/availability?checkIn=2024-06-21&checkOut=2024-06-22&adults=2&children=0&infants=0&payWith=cash'

    data = await fetch_room_data(page_url, api_url)

    if data:
        with open('response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        extract_and_save_data(data)
    else:
        print("Failed to fetch room data.")

    hotels_id, check_in, check_out = extract_url_params(page_url)
    checkin_checkout_dates = generate_checkin_checkout_dates(hotels_id, check_in, 25)
    save_to_csv(checkin_checkout_dates, 'Checkin_Checkout/checkin_checkout_dates.csv')


if __name__ == '__main__':
    asyncio.run(main())
