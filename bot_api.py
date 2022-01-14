from sc2 import *
import sc2
from sc2 import position
from sc2.constants import UnitTypeId, AbilityId, UpgradeId


class bot_api(sc2.BotAI):
    async def has_ability(
            self,
            ability: AbilityId,
            unit):
        unit_ability = await self.get_available_abilities(unit)
        if ability in unit_ability:
            return True
        else:
            return False

    async def train_(
            self,
            unit: UnitTypeId,
            building: UnitTypeId
    ):
        for building in self.structures(building).ready.idle:
            if self.can_afford(unit):
                self.do(building.train(unit))
                break

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

    async def build_(
            self,
            building: UnitTypeId,
            position
    ):
        if self.can_afford(building):
            await self.build(building, near=position)

    async def count(self, building: UnitTypeId):  # For buildings
        ready = self.structures(building).ready.amount
        pending = self.already_pending(building)
        if building == UnitTypeId.GATEWAY or building == UnitTypeId.WARPGATE:
            ready = self.structures(UnitTypeId.GATEWAY).ready.amount + self.structures(UnitTypeId.WARPGATE).ready.amount
            pending = self.already_pending(UnitTypeId.GATEWAY) + self.already_pending(UnitTypeId.WARPGATE)
        return ready + pending

    async def count_(self, unit: UnitTypeId):  # For units
        ready = self.units(unit).ready.amount
        pending = self.already_pending(unit)
        return ready + pending

    async def build_assimilator_(self):
        global Vespene
        if self.structures(UnitTypeId.NEXUS).ready.exists:
            for Nexus in self.structures(UnitTypeId.NEXUS).ready:
                Vespene = self.vespene_geyser.closer_than(9.0, Nexus).filter \
                    (lambda vaspene: not self.structures(UnitTypeId.ASSIMILATOR).closer_than(0.5, vaspene.position))
        for vespene in Vespene:
            worker = self.units(UnitTypeId.PROBE).ready.closest_to(vespene.position)
            if worker != None and self.can_afford(UnitTypeId.ASSIMILATOR):
                self.do(worker.build(UnitTypeId.ASSIMILATOR, vespene))
                break

    async def macro_attack(self, attack_unit):

        enemy_air = self.enemy_units.flying

        if len(self.enemy_units) > 0:
            if attack_unit.weapon_cooldown != 0 or attack_unit.is_attacking:
                self.do(attack_unit.move(self.enemy_units.closest_to(attack_unit.position).position.towards(
                    attack_unit.position, attack_unit.ground_range + 2
                )))
            else:
                if len(enemy_air) > 0:
                    self.do(attack_unit.attack(enemy_air.closest_to(attack_unit.position)))
                else:
                    self.do(attack_unit.attack(self.enemy_units.closest_to(attack_unit.position)))
        elif len(self.enemy_structures) > 0:
            self.do(attack_unit.attack(self.enemy_structures.closest_to(attack_unit.position)))
        else:
            self.do(attack_unit.attack(self.enemy_start_locations[0]))

    async def macro_defend(self, attack_unit):
        half_map = self.start_location.position.distance_to(self.enemy_start_locations[0].position)
        enemy_attack = self.enemy_units.filter(lambda unit: unit.distance_to(self.start_location) < 0.4 * half_map) + \
                       self.enemy_structures.filter(lambda unit: unit.distance_to(self.start_location) < 0.4 * half_map)
        rally_position = self.structures(sc2.UnitTypeId.PYLON).ready.closest_to(self.enemy_start_locations[0]). \
            position.towards(self.game_info.map_center, 10)
        if len(enemy_attack) > 0:
            if attack_unit.weapon_cooldown != 0:
                if self.enemy_units.exists:
                    self.do(attack_unit.move(self.enemy_units.closest_to(attack_unit.position).position.towards(
                        attack_unit.position, attack_unit.ground_range + 1
                    )))
                else:
                    self.do(attack_unit.move(self.enemy_structures.closest_to(attack_unit.position).position.towards(
                        attack_unit.position, attack_unit.ground_range + 1
                    )))
            else:
                if self.enemy_units.exists:
                    self.do(attack_unit.attack(self.enemy_units.closest_to(attack_unit.position)))
                else:
                    self.do(attack_unit.attack(self.enemy_structures.closest_to(attack_unit.position)))
        else:
            if attack_unit.distance_to(rally_position) > 8:
                self.do(attack_unit.move(rally_position))

    async def attack_control_a(self,
                               attack_unit,
                               attack: bool
                               ):  # Defend
        if attack:
            await self.macro_attack(attack_unit)
        else:
            await self.macro_defend(attack_unit)

    async def attack_control_b(self,
                               attack_unit,
                               attack: bool
                               ):
        if attack:
            await self.macro_attack(attack_unit)
        else:
            if attack_unit.shield_percentage > 0.4 and \
                    self.supply_used < 52:
                await self.macro_attack(attack_unit)
            else:
                await self.macro_defend(attack_unit)

    async def attack_control_c(self,
                               attack_unit,
                               attack: bool):  # Harass
        if attack:
            if attack_unit.shield_percentage > 0.2:
                await self.macro_attack(attack_unit)
            else:
                await self.macro_defend(attack_unit)
        else:
            await self.macro_defend(attack_unit)

    async def enemy_in_range(self, known_enemy_list, unit):
        enemy_in_range_list = []
        for enemy in known_enemy_list:
            if unit.distance_to(enemy) <= max(unit.ground_range, unit.air_range) + 2:
                enemy_in_range_list.append(enemy)
        return enemy_in_range_list
