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

from botapi import BotApi


class StalkerColossus(BotApi):
    warp = False

    async def two_base(self):
        if self.structures(UnitTypeId.NEXUS).exists:

            pylon_position = self.structures(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center, 9.2)

            if self.supply_workers < 14:
                await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
            elif self.supply_workers == 14 and await self.count(UnitTypeId.PYLON) < 1:
                await self.build_(UnitTypeId.PYLON, pylon_position)
            elif self.supply_workers < 16:
                await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
            if self.structures(UnitTypeId.PYLON).ready.exists:
                nexus = self.structures(UnitTypeId.NEXUS).ready.first
                if not nexus.is_idle:
                    self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
            if self.structures(UnitTypeId.GATEWAY).exists:
                if self.supply_workers < 19:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 19:
                    if self.can_afford(UnitTypeId.NEXUS):
                        await self.expand_now()
                    if self.structures(UnitTypeId.PYLON).ready.exists and self.structures(UnitTypeId.NEXUS).amount > 1:
                        if not self.structures(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(
                                UnitTypeId.CYBERNETICSCORE):
                            pylon = self.structures(UnitTypeId.PYLON).ready.random
                            await self.build_(UnitTypeId.CYBERNETICSCORE, pylon)
            if self.structures(UnitTypeId.CYBERNETICSCORE).exists:
                if self.supply_workers < 20:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 20 and await self.count(UnitTypeId.ASSIMILATOR) < 2:
                    await self.build_assimilator_()
                elif self.supply_workers < 21:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 21 and await self.count(UnitTypeId.PYLON) < 2:
                    await self.build_(UnitTypeId.PYLON, pylon_position)
                elif await self.count(UnitTypeId.PYLON) == 2:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)

            if self.structures(UnitTypeId.PYLON).ready.exists:
                if not self.structures(UnitTypeId.GATEWAY).exists and not self.already_pending(UnitTypeId.GATEWAY):
                    pylon = self.structures(UnitTypeId.PYLON).ready.random
                    await self.build_(UnitTypeId.GATEWAY, pylon)
            if self.structures(UnitTypeId.GATEWAY).exists and await self.count(UnitTypeId.ASSIMILATOR) < 1:
                await self.build_assimilator_()

    async def stalker_colossus(self):
        await self.distribute_workers()
        await self.train_probe()

        await self.build_nexus()

        await self.build_pylon()
        await self.build_gateway()
        await self.build_assimilator()

        await self.build_cyberneticscore()
        await self.build_twilightcouncil()
        await self.build_roboticsfacility()
        await self.build_roboticsbay()

        await self.train_stalker()
        await self.train_sentry()

    async def train_probe(self):
        if await self.count(UnitTypeId.PROBE) < min(self.townhalls.ready.amount * 22, 68):
            await self.train_(UnitTypeId.NEXUS, UnitTypeId.PROBE)

    async def build_pylon(self):
        position = self.townhalls.first.position.towards(self.game_info.map_center, 9.2)
        potential_supply = self.already_pending(UnitTypeId.PYLON) * 8
        supply_consume = (self.structures(UnitTypeId.GATEWAY).amount + self.structures(
            UnitTypeId.WARPGATE).amount) * 2 + \
                         self.structures(UnitTypeId.ROBOTICSBAY).amount * 6
        if self.supply_left + potential_supply < supply_consume:
            await self.build_(UnitTypeId.PYLON, position)

    async def build_gateway(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        time_constant = self.time / 120
        gateway_num = int(await max(self.count(UnitTypeId.NEXUS), 4) * min(time_constant, 4))
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.GATEWAY) + await self.count(UnitTypeId.WARPGATE) < gateway_num:
            await self.build_(UnitTypeId.GATEWAY, pylon)

    async def build_nexus(self):
        if self.townhalls.amount == 1 and not self.structures(UnitTypeId.ASSIMILATOR).ready.exists:
            return
        if self.townhalls.amount == 2 and not self.structures(UnitTypeId.ROBOTICSFACILITY).ready.eixsts:
            return
        if self.can_afford(UnitTypeId.NEXUS) and not self.already_pending(UnitTypeId.NEXUS):
            await self.expand_now()

    async def build_assimilator(self):
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return
        time_constant = min(2.0, max(1.0, self.time / 180))
        if await self.count(UnitTypeId.ASSIMILATOR) < int(await self.count(UnitTypeId.NEXUS) * time_constant):
            await self.build_assimilator_()

    async def build_cyberneticscore(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            await self.build_(UnitTypeId.CYBERNETICSCORE, pylon)

    async def build_roboticsfacility(self):  # For Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return
        time_constant = self.time // 200
        roboticsfacility_num = int(await self.count(UnitTypeId.NEXUS) - 1) * time_constant
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.ROBOTICSFACILITY) < roboticsfacility_num:
            await self.build_(UnitTypeId.ROBOTICSFACILITY, pylon)

    async def build_roboticsbay(self):  # For Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.ROBOTICSFACILITY).ready.exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.ROBOTICSBAY) < 1:
            await self.build_(UnitTypeId.ROBOTICSBAY, pylon)

    async def build_twilightcouncil(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return
        time_constant = min(self.time // 150, 1)
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.TWILIGHTCOUNCIL) < time_constant:
            await self.build_(UnitTypeId.TWILIGHTCOUNCIL, pylon)

    async def train_sentry(self):
        if not self.warp:
            if await self.count(UnitTypeId.STALKER) >= 2:
                await self.train_(UnitTypeId.SENTRY, UnitTypeId.GATEWAY)
        else:
            if await self.count(UnitTypeId.SENTRY) < await self.count(UnitTypeId.STALKER) * 0.1:  # Need Refinement
                await self.warp_in(UnitTypeId.SENTRY)

    async def train_stalker(self):
        if not self.warp:
            if await self.count(UnitTypeId.STALKER) < 2:
                await self.train_(UnitTypeId.STALKER, UnitTypeId.GATEWAY)
        else:
            if await self.count(UnitTypeId.STALKER) < await self.count(
                    UnitTypeId.COLOSSUS) * 3 + 6:  # Need Refinement
                await self.warp_in(UnitTypeId.STALKER)

    async def operation_cyberneticscore(self):  # For Ground Units
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.warp = True
            elif self.can_afford(AbilityId.RESEARCH_WARPGATE):
                self.do(cyberneticscore(AbilityId.RESEARCH_WARPGATE))

    async def operation_twilightcouncil(self):
        for twilightcouncil in self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_BLINK, twilightcouncil):
                if self.can_afford(AbilityId.RESEARCH_BLINK):
                    self.do(twilightcouncil(AbilityId.RESEARCH_BLINK))
            else:
                if self.can_afford(AbilityId.RESEARCH_CHARGE):
                    self.do(twilightcouncil(AbilityId.RESEARCH_CHARGE))

    async def operation_roboticsbay_vb(self):
        for roboticsbay in self.structures(UnitTypeId.ROBOTICSBAY).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE, roboticsbay):
                if self.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE):
                    self.do(roboticsbay(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE))

    async def build_forge_vb(self):  # Stalker & Colossus
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSBAY).exists:
            if await self.count(UnitTypeId.FORGE) < 2:
                await self.build_(UnitTypeId.FORGE, pylon.position)

    async def operation_forge_vb(self):
        for forge in self.structures(UnitTypeId.FORGE).ready.idle:
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1))
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                    return