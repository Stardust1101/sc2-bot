import sc2
from sc2 import *
from sc2.constants import UnitTypeId, AbilityId, BuffId
from sc2 import Race

from start import *
from mid import *
from bot_api import *


class BotStardust(start, Mid, bot_api):
    async def on_step(self, iteration):
        await self.stalker_colossus_full()

    async def stalker_colossus_full(self):
        if self.supply_workers < 22:
            await self.two_base()
        else:
            await self.stalker_colossus()

    async def one_base_four_gateway_full(self):
        await self.one_base_four_gateway_mid()
