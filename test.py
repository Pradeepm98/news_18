import aiohttp
import asyncio
from api.new_test_transfermart import get_next_match_club

async def process_for_upcoming_match_by_id(name: str, id: str, isClub: bool):
    result = await get_next_match_club(name)
    upcoming_match = ''
    if result['search_result'][120] :
        upcoming_match = result['search_result'][120]
    upcoming_match['upcoming_match']
    print(upcoming_match)

    

if __name__ == "__main__":
    asyncio.run(process_for_upcoming_match_by_id('FC Barcelona', '2911', True))
