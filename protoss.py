from abc import abstractmethod

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId

from sc2.position import Point2
import random

from bot_api import BotApi


class Protoss(BotApi):
    warp = False
    attack_troop = []
    defend_troop = []

    @abstractmethod
    async def economy(self):
        pass

    @abstractmethod
    async def tech(self):
        pass

    @abstractmethod
    async def troop(self):
        pass

    @abstractmethod
    async def train_probe(self):
        pass

    async def build_pylon(self):
        if not self.townhalls.ready.exists:
            return
        position = self.townhalls.first.position.towards(self.game_info.map_center, random.randint(9, 13))
        potential_supply = self.already_pending(UnitTypeId.PYLON) * 8

        supply_consume = self.structures(UnitTypeId.GATEWAY).amount * 2 + \
                         self.structures(UnitTypeId.WARPGATE).amount * 2 + \
                         self.structures(UnitTypeId.ROBOTICSBAY).amount * 6 + \
                         self.townhalls.amount
        if self.supply_left + potential_supply <= min(supply_consume, 200 - self.supply_used):
            await self.build_(UnitTypeId.PYLON, position)

    @abstractmethod
    async def build_gateway(self):
        pass

    @abstractmethod
    async def build_nexus(self):
        pass

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
        if not self.units(UnitTypeId.STALKER).ready.exists:
            return
        time_constant = min(self.time // 150, 1)
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.TWILIGHTCOUNCIL) < time_constant:
            await self.build_(UnitTypeId.TWILIGHTCOUNCIL, pylon)

    async def build_templararchive(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
            return
        if self.vespene > 250:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if await self.count_building(UnitTypeId.TEMPLARARCHIVE) < 1:
                await self.build_(UnitTypeId.TEMPLARARCHIVE, pylon)

    async def train_sentry(self, k=0.03, b=1):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) >= 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.SENTRY)
        else:
            sentry_amount = self.supply_army * k / 2 + b
            if await self.count_unit(UnitTypeId.SENTRY) < sentry_amount:
                await self.warp_in(UnitTypeId.SENTRY)

    async def train_stalker(self, k=0.33, b=1):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) < 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.STALKER)
        else:
            stalker_amount = self.supply_army * k / 2 + b
            if await self.count_unit(UnitTypeId.STALKER) < stalker_amount:
                await self.warp_in(UnitTypeId.STALKER)

    async def train_zealot(self, k=0.2, b=1):
        if self.warp:
            zealot_amount = self.supply_army * k / 2 + b
            if await self.count_unit(UnitTypeId.ZEALOT) < zealot_amount:
                await self.warp_in(UnitTypeId.ZEALOT)

    async def train_colossus(self, k=0.25, b=1):
        if self.structures(UnitTypeId.ROBOTICSBAY).ready.exists:
            colossus_amount = self.supply_army * k / 6 + b
            if await self.count_unit(UnitTypeId.COLOSSUS) < colossus_amount:
                await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.COLOSSUS)

    async def train_immortal(self, k=0.19, b=1):
        immortal_amount = self.supply_army * k / 4 + b
        if await self.count_unit(UnitTypeId.IMMORTAL) < immortal_amount:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.IMMORTAL)

    async def train_hightemplar(self, vespene_threshold=250):
        if self.vespene >= vespene_threshold:
            await self.warp_in(UnitTypeId.HIGHTEMPLAR)

    async def train_observer(self):
        if await self.count_unit(UnitTypeId.OBSERVER) < 1:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.OBSERVER)
        elif await self.count_unit(UnitTypeId.OBSERVER) < 2 and \
            (await self.count_unit(UnitTypeId.IMMORTAL) > 0 or self.supply_used > 150):
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.OBSERVER)

    async def operation_cyberneticscore(self):
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.warp = True
            elif self.can_afford(AbilityId.RESEARCH_WARPGATE):
                cyberneticscore(AbilityId.RESEARCH_WARPGATE)

    # Still need to consider about the order of upgrade
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

    async def build_forge(self):  # Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSBAY).exists:
            if await self.count_building(UnitTypeId.FORGE) < 2:
                await self.build_(UnitTypeId.FORGE, pylon.position)

    async def operation_nexus(self):
        structures = \
            self.structures(UnitTypeId.GATEWAY) + \
            self.structures(UnitTypeId.ROBOTICSFACILITY) + \
            self.structures(UnitTypeId.WARPGATE) + \
            self.structures(UnitTypeId.CYBERNETICSCORE)
        idle_structures = \
            self.structures(UnitTypeId.GATEWAY).idle + \
            self.structures(UnitTypeId.ROBOTICSFACILITY).idle + \
            self.structures(UnitTypeId.WARPGATE).idle + \
            self.structures(UnitTypeId.CYBERNETICSCORE).idle
        working_structures = structures - idle_structures
        if len(working_structures) == 0:
            return
        for nexus in self.structures(UnitTypeId.NEXUS).ready:
            if await self.has_ability(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus):
                for structure in working_structures:
                    if not structure.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, structure)

    async def operation_forge(self):
        for forge in self.structures(UnitTypeId.FORGE).ready.idle:
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1):
                    forge(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2):
                    forge(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3):
                    forge(AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3)
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

    async def operation_sentry(self):
        for sentry in self.units(UnitTypeId.SENTRY):
            if sentry in self.defend_troop:
                await self.defend(sentry)
            elif sentry in self.attack_troop:
                await self.attack(sentry)

            if self.enemy_units.closer_than(8, sentry.position):
                if not sentry.has_buff(BuffId.GUARDIANSHIELD):
                    if await self.can_cast(sentry, AbilityId.GUARDIANSHIELD_GUARDIANSHIELD):
                        sentry(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD)
                        return

    async def operation_general_troop(self, unit: UnitTypeId, distance: int = 1):
        for unit in self.units(unit):
            if unit in self.defend_troop:
                await self.defend(unit)
            elif unit in self.attack_troop:
                await self.attack(unit)

    async def operation_observer(self):
        if not self.units(UnitTypeId.STALKER).ready.exists:
            return
        cloaked = self.enemy_units.filter(lambda unit: unit.is_cloaked)
        for observer in self.units(UnitTypeId.OBSERVER).ready.filter(
                lambda unit: not self.has_order([AbilityId.PATROL], unit)):
            if cloaked.amount > 0:
                observer.move(cloaked.closest_to(self.start_location).position.towards(
                    self.townhalls.first, 3))
            else:
                observer.move(self.units(UnitTypeId.STALKER).closest_to(self.enemy_start_locations[0]).position.towards(
                    self.townhalls.first, 2))

    @abstractmethod
    async def operation_hightemplar(self):
        pass

    @abstractmethod
    async def CONTROL_ATTACK(self):
        pass

    @abstractmethod
    async def CONTROL_PANIC(self):
        pass

    async def random_scout(self):
        units_to_ignore = [UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.EGG, UnitTypeId.LARVA,
                           UnitTypeId.OVERLORD, UnitTypeId.OVERSEER, UnitTypeId.OBSERVER]
        detect_units = [UnitTypeId.OBSERVER, UnitTypeId.PHOTONCANNON, UnitTypeId.OVERSEER, UnitTypeId.RAVEN,
                        UnitTypeId.MISSILETURRET, UnitTypeId.SPORECRAWLER, UnitTypeId.SPORECANNON]
        # Due to the return problem, the scouting worker is commented
        """
        if self.units(UnitTypeId.PROBE).ready.amount > 22:
            scout_worker = None
            for worker in self.workers:
                if self.has_order([AbilityId.PATROL], worker):
                    scout_worker = worker
            if not scout_worker:
                random_exp_location = random.choice(self.expansion_locations_list)
                if self.units(UnitTypeId.OBSERVER).ready.amount == 0:
                    scout_worker = self.workers.closest_to(self.start_location)
                if not scout_worker:
                    return
                await self.order(scout_worker, AbilityId.PATROL, random_exp_location)
                return
            nearby_enemy_units = self.enemy_units.filter(lambda unit: unit.type_id not in units_to_ignore).closer_than(
                10, scout_worker)
            if nearby_enemy_units.exists:
                await self.order(scout_worker, AbilityId.PATROL, self.game_info.map_center)
                return
            target = Point2((scout_worker.orders[0].target.x, scout_worker.orders[0].target.y))
            if scout_worker.distance_to(target) < 10:
                random_exp_location = random.choice(self.expansion_locations_list)
                await self.order(scout_worker, AbilityId.PATROL, random_exp_location)
                return
        """
        if self.units(UnitTypeId.OBSERVER).ready.amount >= 1:
            scout = None
            for observer in self.units(UnitTypeId.OBSERVER):
                if self.has_order([AbilityId.PATROL], observer):
                    scout = observer
            if not scout:
                random_exp_location = random.choice(self.expansion_locations_list)
                scout = self.units(UnitTypeId.OBSERVER).closest_to(self.start_location)
                if not scout:
                    return
                await self.order(scout, AbilityId.PATROL, random_exp_location)
                return
            if self.enemy_units.filter(lambda unit: unit.type_id in detect_units).closer_than(10, scout):
                await self.order(scout, AbilityId.PATROL, self.game_info.map_center)
                return
            target = Point2((scout.orders[0].target.x, scout.orders[0].target.y))
            if scout.distance_to(target) < 10:
                random_exp_location = random.choice(self.expansion_locations_list)
                await self.order(scout, AbilityId.PATROL, random_exp_location)

                return

    async def cancel_building(self):
        for structure in self.structures(UnitTypeId.NEXUS).not_ready.filter(
                lambda unit: unit.shield_percentage == 0 and unit.health_percentage < 0.2):
            if await self.has_ability(AbilityId.CANCEL, structure):
                structure(AbilityId.CANCEL)



