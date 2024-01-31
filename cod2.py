import aiohttp
import asyncio
import folium
async def get_info_by_ip(ip="127.0.0.1"):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://ip-api.com/json/{ip}") as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if data.get("status") == "fail":
                            return f"Failed to get information for IP {ip}. Reason: {data.get('message')}"
                        else:
                            return data
                            # rest of your code

                    except aiohttp.ContentTypeError:
                        return f"Failed to decode JSON response for IP {ip}"

                else:
                    return f"Failed to get information for IP {ip}. Status code: {response.status}"

    except aiohttp.ClientError:
        return "An error occurred with the HTTP client."

async def main():
    result = await get_info_by_ip(input())
    print(result)

if __name__ == "__main__":
    asyncio.run(main())