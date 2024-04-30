import asyncio
from time import time, sleep
from typing import Iterator

from utils.general.utils.timer import timer


class TimePointList:

    def __init__(self):
        self.__deltas = []
        self.__first_point: float | None = None
        self.__last_point: float | None = None

    def __iter__(self) -> Iterator[float]:
        if self.__first_point is None:
            return

        current_point = self.__first_point
        yield current_point

        for delta in self.__deltas:
            current_point += delta
            yield current_point

    def __len__(self) -> int:
        if self.__first_point is None:
            return 0

        return len(self.__deltas) + 1

    def get_last_point(self) -> float | None:
        return self.__last_point

    def delete(self, index: int) -> None:
        if self.__first_point is None:
            return

        if index == len(self.__deltas):
            self.__first_point = None
            self.__last_point = None
            self.__deltas.clear()
            return

        for i, element in enumerate(self.__iter__()):
            if i == index:
                self.__first_point = element
                break

        del self.__deltas[:index]

    def append(self, point: float) -> None:
        if self.__first_point is None:
            self.__first_point = point
        else:
            self.__deltas.append(point - self.__last_point)

        self.__last_point = point


class TimeCounter:

    def __init__(self, *, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0):
        self.__interval = int(timer(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds))

        self.__list = TimePointList()

    def __check(self) -> None:
        current_index: int | None = None

        for index, element in enumerate(self.__list):
            if time() - element <= self.__interval:
                break

            current_index = index

        if current_index is not None:
            self.__list.delete(current_index)

    def add(self):
        self.__check()
        self.__list.append(time())
        return len(self.__list)

    @property
    def time_until_element_is_deleted(self) -> float:
        return self.__interval - (time() - (self.__list.get_last_point() or 0))


class FloodControl:

    def __init__(self, n_times_per_period, *, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0):
        self.__n_times_per_period = n_times_per_period
        self.__interval = int(timer(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds))

        self.__list = TimePointList()

    def __check(self) -> None:
        current_index: int | None = None

        for index, element in enumerate(self.__list):
            if time() - element <= self.__interval:
                break

            current_index = index

        if current_index is not None:
            self.__list.delete(current_index)

    @property
    def time_until_element_is_deleted(self) -> float:
        return self.__interval - (time() - (self.__list.get_last_point() or 0))

    def add(self) -> bool:
        self.__check()

        result = True

        if len(self.__list) + 1 > self.__n_times_per_period:
            result = False

        self.__list.append(time())
        return result

    async def async_wait_point(self):
        self.__check()

        if len(self.__list) + 1 > self.__n_times_per_period:
            await asyncio.sleep(self.time_until_element_is_deleted)

        self.__list.append(time())

    def sync_wait_point(self):
        self.__check()

        if len(self.__list) + 1 > self.__n_times_per_period:
            sleep(self.time_until_element_is_deleted)

        self.__list.append(time())
