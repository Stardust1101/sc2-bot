import sc2
from sc2 import *
from sc2.constants import UnitTypeId, AbilityId, BuffId, UpgradeId

from bot_api import bot_api


# Now there should be 2 Nexus, a cybernetics core, a gateway, 2 pylons and 23 probes
# Let's get started
class Mid(bot_api):
    async def stalker_colossus(self):

        global warp
        warp = False

        await self.distribute_workers(resource_ratio=1.6)
        await self.build_pylon_vb()
        await self.build_nexus_vb()
        await self.CONTROLL_ATTACK_vb()

        if self.structures(UnitTypeId.PYLON).ready.exists:
            await self.build_gateway_vb()
            await self.build_assimilator_vb()
            if await self.count_(UnitTypeId.STALKER) > 1:
                await self.build_twilightcouncil_vb()
                await self.build_roboticsfacility_vb()
            await self.build_roboticsbay_vb()
            await self.build_forge_vb()

        await self.operation_cyberneticscore_vb()  # Must before any gateway operation
        await self.operation_twilightcouncil_vb()
        await self.operation_roboticsbay_vb()
        await self.operation_stalker_vb()
        await self.operation_colossus_vb()
        await self.operation_forge_vb()
        await self.operation_zealot_vb()
        await self.operation_sentry_vb()
        await self.train_probe_vb()
        await self.train_stalker_vb()
        await self.train_zealot_vb()
        await self.train_colossus_vb()
        await self.train_sentry_vb()

    # _vb is stalker_colossus
    async def train_probe_vb(self):
        if self.supply_workers < min(await self.count(UnitTypeId.NEXUS) * 22, 66):
            await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)

    async def build_pylon_vb(self):
        pylon_position = self.structures(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center, 9.2)
        potential_supply = self.already_pending(UnitTypeId.PYLON) * 8
        supply_consume = (self.structures(UnitTypeId.GATEWAY).amount + self.structures(
            UnitTypeId.WARPGATE).amount) * 2 + \
                         self.structures(UnitTypeId.ROBOTICSBAY).amount * 6
        if self.supply_left + potential_supply < supply_consume:
            await self.build_(UnitTypeId.PYLON, pylon_position)

    async def build_nexus_vb(self):  # Stalker & Colossus
        if self.can_afford(UnitTypeId.NEXUS) and not self.already_pending(UnitTypeId.NEXUS):
            await self.expand_now()

    async def build_gateway_vb(self):
        time_constant = self.time / 200
        gateway_num = int(await self.count(UnitTypeId.NEXUS) * min(time_constant, 3)) + 1
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.GATEWAY) + await self.count(UnitTypeId.WARPGATE) < gateway_num:
            await self.build_(UnitTypeId.GATEWAY, pylon)

    async def build_roboticsfacility_vb(self):  # For Stalker & Colossus
        roboticsfacility_num = int(await self.count(UnitTypeId.NEXUS) - 1)
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.ROBOTICSFACILITY) < roboticsfacility_num:
            await self.build_(UnitTypeId.ROBOTICSFACILITY, pylon)

    async def build_roboticsbay_vb(self):  # For Stalker & Colossus
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.ROBOTICSBAY) < 1:
            await self.build_(UnitTypeId.ROBOTICSBAY, pylon)

    async def build_twilightcouncil_vb(self):
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count(UnitTypeId.TWILIGHTCOUNCIL) < 1:
            await self.build_(UnitTypeId.TWILIGHTCOUNCIL, pylon)

    async def build_assimilator_vb(self):
        if await self.count(UnitTypeId.ASSIMILATOR) < int(await self.count(UnitTypeId.NEXUS) * 1.5):
            await self.build_assimilator_()

    async def train_stalker_vb(self):
        if warp == False:
            if await self.count_(UnitTypeId.STALKER) < 2:
                await self.train_(UnitTypeId.STALKER, UnitTypeId.GATEWAY)
        else:
            if await self.count_(UnitTypeId.STALKER) < await self.count_(
                    UnitTypeId.COLOSSUS) * 3 + 6:  # Need Refinement
                await self.warp_in(UnitTypeId.STALKER)

    async def train_zealot_vb(self):
        if warp:
            if await self.count_(UnitTypeId.ZEALOT) < await self.count_(UnitTypeId.STALKER) * 0.3:  # Need Refinement
                await self.warp_in(UnitTypeId.ZEALOT)

    async def train_sentry_vb(self):
        if warp:
            if await self.count_(UnitTypeId.SENTRY) < await self.count_(UnitTypeId.STALKER) * 0.1:  # Need Refinement
                await self.warp_in(UnitTypeId.SENTRY)

    async def train_colossus_vb(self):
        if self.structures(UnitTypeId.ROBOTICSBAY).ready.exists:
            await self.train_(UnitTypeId.COLOSSUS, UnitTypeId.ROBOTICSFACILITY)

    async def operation_cyberneticscore_vb(self):  # For Ground Units

        global warp
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if self.can_afford(AbilityId.RESEARCH_WARPGATE) and \
                    await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.do(cyberneticscore(AbilityId.RESEARCH_WARPGATE))
            elif not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                warp = True

        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
                if self.can_afford(AbilityId.RESEARCH_WARPGATE) and \
                        await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                    self.do(cyberneticscore(AbilityId.RESEARCH_WARPGATE))

    async def operation_twilightcouncil_vb(self):
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
            for twilightcouncil in self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.idle:
                if self.can_afford(AbilityId.RESEARCH_BLINK) and \
                        await self.has_ability(AbilityId.RESEARCH_BLINK, twilightcouncil):
                    self.do(twilightcouncil(AbilityId.RESEARCH_BLINK))

    async def operation_roboticsbay_vb(self):
        if self.structures(UnitTypeId.ROBOTICSBAY).ready.exists:
            for roboticsbay in self.structures(UnitTypeId.ROBOTICSBAY).ready.idle:
                if self.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE) and \
                        await self.has_ability(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE, roboticsbay):
                    self.do(roboticsbay(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE))

    async def operation_stalker_vb(self):  # Stalker & Colossus
        for stalker in self.units(UnitTypeId.STALKER):
            enemy_in_range = await self.enemy_in_range(self.enemy_units, stalker)
            await self.attack_control_b(stalker, attack)
            if await self.has_ability(AbilityId.EFFECT_BLINK_STALKER, stalker):
                if stalker.shield_percentage <= 0.4 and len(enemy_in_range) != 0:
                    self.do(stalker(
                        AbilityId.EFFECT_BLINK_STALKER,
                        self.enemy_units.closest_to(stalker.position).position.towards(
                            stalker.position, 14
                        )))

    async def operation_zealot_vb(self):  # Stalker & Colossus
        for zealot in self.units(UnitTypeId.ZEALOT):
            await self.attack_control_c(zealot, attack)

    async def operation_sentry_vb(self):  # Stalker & Colossus
        for sentry in self.units(UnitTypeId.SENTRY):

            enemy_in_range = await self.enemy_in_range(self.enemy_units, sentry)

            await self.attack_control_c(sentry, attack)
            if len(enemy_in_range) > 0:
                if await self.can_cast(sentry, AbilityId.GUARDIANSHIELD_GUARDIANSHIELD):
                    self.do(sentry(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD))
                elif await self.can_cast(sentry, AbilityId.FORCEFIELD_FORCEFIELD) and \
                        not await self.can_cast(sentry, AbilityId.FORCEFIELD_CANCEL):
                    self.do(sentry(AbilityId.FORCEFIELD_FORCEFIELD, self.enemy_units.closest_to(sentry)))

    async def operation_colossus_vb(self):
        for colossus in self.units(sc2.UnitTypeId.COLOSSUS):
            await self.attack_control_c(colossus, attack)

    async def build_forge_vb(self):  # Stalker & Colossus
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSBAY).exists:
            if await self.count(UnitTypeId.FORGE) < 2:
                await self.build_(UnitTypeId.FORGE, pylon.position)

    async def operation_forge_vb(self):
        if self.structures(UnitTypeId.FORGE).ready.exists:
            for forge in self.structures(UnitTypeId.FORGE).ready.idle:
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1) and await self.has_ability(
                        AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, forge):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1))
                    break
                elif self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2) and await self.has_ability(
                        AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, forge):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                    break
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1) and await self.has_ability(
                        AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, forge):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                    break
                elif self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2) and await self.has_ability(
                        AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, forge):
                    self.do(forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                    break

    async def CONTROLL_ATTACK_vb(self):
        global attack
        global attack_history
        if self.supply_workers < 24:
            attack_history = False
            attack = False
        if self.units(UnitTypeId.STALKER).ready.exists:
            if await self.has_ability(AbilityId.EFFECT_BLINK_STALKER, self.units(UnitTypeId.STALKER).first):
                attack_history = True
        if attack_history:
            if await self.count_(UnitTypeId.STALKER) > 16:
                attack = True
