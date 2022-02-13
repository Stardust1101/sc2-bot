import sc2
from sc2 import position
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2
from sc2.player import Bot, Computer

from sc2.bot_ai import BotAI
from sc2.data import Race


class BotApi(BotAI):
    async def train_(self, building: UnitTypeId, unit: UnitTypeId):
        if building in [UnitTypeId.NEXUS]:
            for nexus in self.townhalls.ready.idle:
                if self.can_afford(unit):
                    nexus.train(unit)
                    return
        else:
            for building in self.structures(building).ready.idle:
                if self.can_afford(unit):
                    building.train(unit)
                    return

    async def build_(self, building: UnitTypeId, position: Point2):
        if self.can_afford(building):
            await self.build(building, near=position)

    async def count(self, building: UnitTypeId, count_pending: bool = True) -> int:
        ready = self.structures(building).ready.amount
        pending = self.already_pending(building)
        if building == UnitTypeId.GATEWAY or building == UnitTypeId.WARPGATE:
            ready = self.structures(UnitTypeId.GATEWAY).ready.amount + self.structures(UnitTypeId.WARPGATE).ready.amount
            pending = self.already_pending(UnitTypeId.GATEWAY) + self.already_pending(UnitTypeId.WARPGATE)
        return ready + (count_pending * pending)

    async def build_assimilator_(self):
        if self.structures(UnitTypeId.NEXUS).ready.exists:
            for nexus in self.structures(UnitTypeId.NEXUS):
                geysers = self.vespene_geyser.closer_than(9.0, nexus).filter \
                    (lambda vespene: not self.structures(UnitTypeId.ASSIMILATOR).closer_than(0.5, vespene.position))
                for geyser in geysers:
                    worker = self.units(UnitTypeId.PROBE).ready.closest_to(geyser.position)
                    if worker and self.can_afford(UnitTypeId.ASSIMILATOR):
                        self.do(worker.build(UnitTypeId.ASSIMILATOR, geyser))
                        break

    async def has_ability(self, ability: AbilityId, unit: Units) -> bool:
        unit_ability = await self.get_available_abilities(unit)
        if ability in unit_ability:
            return True
        else:
            return False

    async def warp_in(self,
                      unit: UnitTypeId,
                      location=None):
        import random
        x = random.randrange(-8, 8)
        y = random.randrange(-8, 8)
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready.idle:
            if self.structures(UnitTypeId.PYLON).ready.exists:
                if location is None:
                    position_point = self.structures(UnitTypeId.PYLON).ready.random.position
                    placement = position.Point2((position_point.x + x, position_point.y + y))
                else:
                    placement = position.Point2((location.x + x, location.y + y))
                if self.can_afford(unit):
                    self.do(warpgate.warp_in(unit, placement))

