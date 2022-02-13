import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2
from sc2.player import Bot, Computer

from sc2.bot_ai import BotAI
from sc2.data import Race

from botapi import *
from StalkerColossus import StalkerColossus


class BotStardust(StalkerColossus):
    async def on_step(self, iteration):
        await self.stalker_colossus()


