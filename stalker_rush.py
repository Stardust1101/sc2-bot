from abc import ABC

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId

from protoss import Protoss


class StalkerRush(Protoss, ABC):

    async def train_probe(self):
        if self.supply_workers < 23:
            await self.train_(UnitTypeId.NEXUS, UnitTypeId.PROBE)

