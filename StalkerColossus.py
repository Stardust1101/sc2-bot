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
    attack_troop = []
    defend_troop = []

    async def stalker_colossus(self):
        await self.distribute_workers()
        await self.train_probe()

        await self.build_nexus()

        await self.build_pylon()
        await self.build_gateway()
        await self.build_assimilator()

        await self.build_cyberneticscore()
        await self.train_stalker()
        await self.train_sentry()

        await self.build_twilightcouncil()
        await self.build_roboticsfacility()
        await self.build_roboticsbay()

        await self.operation_cyberneticscore()
        await self.operation_roboticsbay()
        await self.operation_twilightcouncil()

        await self.operation_stalker()
        await self.CONTROL_ATTACK()

    async def train_probe(self):
        if self.supply_workers < min(self.townhalls.ready.amount * 22, 66):
            await self.train_(UnitTypeId.NEXUS, UnitTypeId.PROBE)

    async def build_pylon(self):
        position = self.townhalls.first.position.towards(self.game_info.map_center, 9.2)
        potential_supply = self.already_pending(UnitTypeId.PYLON) * 8

        supply_consume = self.structures(UnitTypeId.GATEWAY).amount * 2 + \
                         self.structures(UnitTypeId.WARPGATE).amount * 2 + \
                         self.structures(UnitTypeId.ROBOTICSBAY).amount * 6 + \
                         self.townhalls.amount
        if self.supply_left + potential_supply < supply_consume:
            await self.build_(UnitTypeId.PYLON, position)

    async def build_gateway(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        time_constant = self.time / 180
        gateway_num = (await self.count_building(UnitTypeId.NEXUS) - 1) * min(time_constant, 4) + 1
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.GATEWAY) + await self.count_building(UnitTypeId.WARPGATE) < gateway_num:
            await self.build_(UnitTypeId.GATEWAY, pylon)

    async def build_nexus(self):
        if self.townhalls.amount == 1 and not self.structures(UnitTypeId.ASSIMILATOR).ready.exists:
            return
        if self.townhalls.amount == 2 and not self.structures(UnitTypeId.ROBOTICSBAY).exists:
            return
        if self.townhalls.amount == 3 and self.supply_army < 60:
            return
        if self.can_afford(UnitTypeId.NEXUS) and not self.already_pending(UnitTypeId.NEXUS):
            await self.expand_now()

    async def build_assimilator(self):
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return
        time_constant = min(2.0, max(1.0, self.time / 180))
        if await self.count_building(UnitTypeId.ASSIMILATOR) < \
                int(await self.count_building(UnitTypeId.NEXUS) * time_constant):
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
        time_constant = min(self.time // 200, 1)
        roboticsfacility_num = int(await self.count_building(UnitTypeId.NEXUS, count_pending=False) - 1) * time_constant
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.ROBOTICSFACILITY) < roboticsfacility_num:
            await self.build_(UnitTypeId.ROBOTICSFACILITY, pylon)

    async def build_roboticsbay(self):  # For Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.ROBOTICSFACILITY).ready.exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.ROBOTICSBAY) < 1:
            await self.build_(UnitTypeId.ROBOTICSBAY, pylon)

    async def build_twilightcouncil(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return
        time_constant = min(self.time // 150, 1)
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.TWILIGHTCOUNCIL) < time_constant:
            await self.build_(UnitTypeId.TWILIGHTCOUNCIL, pylon)

    async def train_sentry(self):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) >= 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.SENTRY)
        else:
            if await self.count_unit(UnitTypeId.SENTRY) < await self.count_unit(
                    UnitTypeId.STALKER) * 0.1:  # Need Refinement
                await self.warp_in(UnitTypeId.SENTRY)

    async def train_stalker(self):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) < 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.STALKER)
        else:
            if await self.count_unit(UnitTypeId.STALKER) < self.time:
                await self.warp_in(UnitTypeId.STALKER)

    async def operation_cyberneticscore(self):  # For Ground Units
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.warp = True
            elif self.can_afford(AbilityId.RESEARCH_WARPGATE):
                cyberneticscore(AbilityId.RESEARCH_WARPGATE)

    async def operation_twilightcouncil(self):
        for twilightcouncil in self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_BLINK, twilightcouncil):
                if self.can_afford(AbilityId.RESEARCH_BLINK):
                    twilightcouncil(AbilityId.RESEARCH_BLINK)
            else:
                if self.can_afford(AbilityId.RESEARCH_CHARGE):
                    twilightcouncil(AbilityId.RESEARCH_CHARGE)

    async def operation_roboticsbay(self):
        for roboticsbay in self.structures(UnitTypeId.ROBOTICSBAY).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE, roboticsbay):
                if self.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE):
                    roboticsbay(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE)

    async def build_forge_vb(self):  # Stalker & Colossus
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSBAY).exists:
            if await self.count_building(UnitTypeId.FORGE) < 2:
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

    async def operation_stalker(self):
        for stalker in self.units(UnitTypeId.STALKER):
            if stalker in self.defend_troop:
                await self.defend(stalker)
            elif stalker in self.attack_troop:
                await self.attack(stalker)
            if not await self.has_ability(AbilityId.EFFECT_BLINK_STALKER, stalker):
                return
            if stalker.shield_percentage <= 0.4 and self.enemy_units.in_attack_range_of(stalker):
                stalker(AbilityId.EFFECT_BLINK_STALKER,
                        self.enemy_units.closest_to(stalker.position).position.towards(stalker.position, 14))

    async def CONTROL_ATTACK(self):
        army = self.units(UnitTypeId.STALKER).ready + self.units(UnitTypeId.SENTRY).ready
        for unit in army:
            if not unit in self.attack_troop and not unit in self.defend_troop:
                self.defend_troop.append(unit)
        if len(self.defend_troop) >= 30:
            self.attack_troop += self.defend_troop
            self.defend_troop = []
        if len(self.attack_troop) <= 5:
            self.defend_troop += self.attack_troop
            self.attack_troop = []
