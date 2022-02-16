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


async def micro_attack(unit: Unit, enemy: Unit, micro: bool = True):
    if not enemy.type_id == UnitTypeId.DISRUPTORPHASED:
        if unit.weapon_cooldown == 0:
            unit.attack(enemy)
        elif unit.weapon_cooldown < 0:
            unit.move(enemy.position.towards(unit.position, 7))
        else:
            if not enemy.is_structure:
                unit.move(enemy.position.towards(unit.position, unit.ground_range + 1))
            else:
                unit.move(enemy.position.towards(unit.position, unit.ground_range - 1))
    else:
        unit.move(enemy.position.towards(unit.position, 12))


async def random(min, max):
    import random
    output = random.randrange(min, max)
    return output


def structure_attack(enemy: Unit):
    return enemy.type_id == UnitTypeId.PHOTONCANNON or enemy.type_id == UnitTypeId.SPINECRAWLER


def is_worker(enemy: Unit):
    return enemy.type_id in [UnitTypeId.PROBE, UnitTypeId.SCV, UnitTypeId.DRONE]


class BotApi(BotAI):

    def has_order(self, orders, unit):
        if type(orders) != list:
            orders = [orders]
        count = 0
        if len(unit.orders) >= 1 and unit.orders[0].ability.id in orders:
            count += 1
        return count

    async def train_(self, building: UnitTypeId, unit: UnitTypeId):
        if building == UnitTypeId.NEXUS:
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

    async def count_building(self, building: UnitTypeId, count_pending: bool = True) -> int:
        ready = self.structures(building).ready.amount
        pending = self.already_pending(building)
        if building == UnitTypeId.GATEWAY or building == UnitTypeId.WARPGATE:
            ready = self.structures(UnitTypeId.GATEWAY).ready.amount + self.structures(UnitTypeId.WARPGATE).ready.amount
            pending = self.already_pending(UnitTypeId.GATEWAY) + self.already_pending(UnitTypeId.WARPGATE)
        return ready + (count_pending * pending)

    async def count_unit(self, unit: UnitTypeId, count_pending: bool = True) -> int:
        ready = self.units(unit).ready.amount
        pending = self.already_pending(unit)
        return ready + (count_pending * pending)

    async def build_assimilator_(self):
        if self.structures(UnitTypeId.NEXUS).ready.exists:
            for nexus in self.structures(UnitTypeId.NEXUS):
                geysers = self.vespene_geyser.closer_than(9.0, nexus).filter \
                    (lambda vespene: not self.structures(UnitTypeId.ASSIMILATOR).closer_than(0.5, vespene.position))
                for geyser in geysers:
                    if self.units(UnitTypeId.PROBE).ready.amount > 1:
                        worker = self.units(UnitTypeId.PROBE).ready.closest_to(geyser.position)
                        if worker and self.can_afford(UnitTypeId.ASSIMILATOR):
                            worker.build(UnitTypeId.ASSIMILATOR, geyser)
                            break

    async def has_ability(self, ability: AbilityId, unit: Units) -> bool:
        unit_ability = await self.get_available_abilities(unit)
        if ability in unit_ability:
            return True
        else:
            return False

    async def warp_in(self, unit: UnitTypeId, location=None):
        import random
        x = random.randrange(-8, 8)
        y = random.randrange(-8, 8)
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            if not await self.has_ability(AbilityId.WARPGATETRAIN_ZEALOT, warpgate):
                continue
            if self.structures(UnitTypeId.PYLON).ready.exists:
                if location is None:
                    position_point = self.structures(UnitTypeId.PYLON).ready.random.position
                    placement = Point2((position_point.x + x, position_point.y + y))
                else:
                    placement = Point2((location.x + x, location.y + y))
                if self.can_afford(unit):
                    warpgate.warp_in(unit, placement)
                    return

    async def defend(self, unit: Unit):
        half_map = self.start_location.position.distance_to(self.enemy_start_locations[0].position)
        enemy_unit = self.enemy_units.filter(
            lambda enemy: enemy.distance_to(self.start_location) < 0.4 * half_map)
        enemy_structure = self.enemy_structures.filter(
            lambda enemy: enemy.distance_to(self.start_location) < 0.4 * half_map)
        rally_position = self.structures(UnitTypeId.PYLON).ready.closest_to(self.enemy_start_locations[0]). \
            position.towards(self.game_info.map_center, 4)
        enemy_offensive = enemy_unit + enemy_structure
        if len(enemy_offensive) != 0:
            await micro_attack(unit, enemy_offensive.closest_to(unit), micro=unit.type_id != UnitTypeId.ZEALOT)
        else:
            if unit.distance_to(rally_position) > 10:
                unit.move(rally_position)

    async def attack(self, unit: Unit):
        enemy = self.enemy_structures + self.enemy_units.filter(lambda unit: unit.can_be_attacked)
        enemy_offensive = self.enemy_units.filter(lambda unit: not is_worker(unit)) + \
                          self.enemy_structures.filter(lambda unit: structure_attack(unit))
        enemy_passive = enemy - enemy_offensive
        if len(enemy_offensive) != 0:
            await micro_attack(unit, enemy_offensive.closest_to(unit), micro=unit.type_id != UnitTypeId.ZEALOT)
        elif len(self.enemy_structures) != 0:
            await micro_attack(unit, enemy_passive.closest_to(unit), micro=unit.type_id != UnitTypeId.ZEALOT)
        else:
            unit.attack(self.enemy_start_locations[0])

    async def order(self, units, order, target=None, silent=True):
        if type(units) != list:
            unit = units
            unit(order, target=target)
        else:
            for unit in units:
                unit(order, target=target)
