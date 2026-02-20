import asyncio
import random
import string
import sys
import time
from collections import deque, defaultdict
from dataclasses import dataclass

import aiohttp
import aiofiles


# ================= CONFIG =================

@dataclass
class Config:
    min_length: int = 4
    max_length: int = 4
    concurrent_connections: int = 50
    timeout: int = 10

    initial_rate: float = 2
    max_rate: float = 15
    min_rate: float = 0.5

    output_file: str = "available_ids.txt"


# ================= RATE LIMITER =================

class RateLimiter:
    def __init__(self, cfg: Config):
        self.rate = cfg.initial_rate
        self.max_rate = cfg.max_rate
        self.min_rate = cfg.min_rate

        self.tokens = self.rate
        self.last = time.monotonic()
        self.lock = asyncio.Lock()

        self.success_streak = 0
        self.hits_429 = 0

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            self.tokens += (now - self.last) * self.rate
            self.tokens = min(self.tokens, self.max_rate)
            self.last = now

            if self.tokens < 1:
                wait = (1 - self.tokens) / self.rate
            else:
                self.tokens -= 1
                return

        await asyncio.sleep(wait)

    async def success(self):
        async with self.lock:
            self.success_streak += 1
            if self.success_streak >= 25:
                self.rate = min(self.max_rate, self.rate + 0.5)
                self.success_streak = 0

    async def hit_429(self):
        async with self.lock:
            self.hits_429 += 1
            self.rate = max(self.min_rate, self.rate * 0.6)
            self.success_streak = 0


# ================= NAME GEN =================

class NameGenerator:
    CHARS = string.ascii_lowercase + string.digits + "_"
    EDGE = string.ascii_lowercase + string.digits

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def next(self):
        length = random.randint(self.cfg.min_length, self.cfg.max_length)

        name = [random.choice(self.CHARS) for _ in range(length)]

        if name[0] == "_":
            name[0] = random.choice(self.EDGE)
        if name[-1] == "_":
            name[-1] = random.choice(self.EDGE)

        return "".join(name)


# ================= CLIENT =================

class MojangClient:
    def __init__(self, cfg: Config, limiter: RateLimiter):
        self.cfg = cfg
        self.limiter = limiter
        self.sem = asyncio.Semaphore(cfg.concurrent_connections)

    async def start(self):
        timeout = aiohttp.ClientTimeout(total=self.cfg.timeout)

        connector = aiohttp.TCPConnector(limit=self.cfg.concurrent_connections, ttl_dns_cache=300)

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": "ID-Hunter/UltraLight"}
        )

    async def close(self):
        await self.session.close()

    async def check(self, name):

        url = f"https://api.mojang.com/users/profiles/minecraft/{name}"

        await self.limiter.acquire()

        async with self.sem:
            try:
                async with self.session.get(url) as r:

                    if r.status == 204:
                        await self.limiter.success()
                        return True

                    if r.status == 200:
                        await self.limiter.success()
                        return False

                    if r.status == 429:
                        await self.limiter.hit_429()

            except (aiohttp.ClientError, asyncio.TimeoutError):
                return None


# ================= ENGINE =================

class Engine:

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.limiter = RateLimiter(cfg)
        self.gen = NameGenerator(cfg)
        self.client = MojangClient(cfg, self.limiter)

        self.checked = 0
        self.found = 0
        self.start = 0

        self.queue = asyncio.Queue(maxsize=cfg.concurrent_connections * 2)

        self.speed_hist = deque(maxlen=30)

    async def worker(self, file):

        while True:
            name = await self.queue.get()

            res = await self.client.check(name)

            self.checked += 1

            if res:
                self.found += 1
                await file.write(name + "\n")

            self.queue.task_done()

    async def producer(self):

        while True:
            await self.queue.put(self.gen.next())

    async def stats(self):

        last = 0

        while True:
            await asyncio.sleep(1)

            speed = self.checked - last
            last = self.checked

            self.speed_hist.append(speed)
            avg = sum(self.speed_hist) / len(self.speed_hist)

            msg = (
                f"\rChecked {self.checked} | "
                f"Found {self.found} | "
                f"{speed}/s | "
                f"Avg {avg:.1f}/s | "
                f"Rate {self.limiter.rate:.2f} | "
                f"429 {self.limiter.hits_429}"
            )

            sys.stdout.write(msg)
            sys.stdout.flush()

    async def run(self):

        self.start = time.monotonic()

        await self.client.start()

        try:
            async with aiofiles.open(self.cfg.output_file, "a") as file:

                workers = [
                    asyncio.create_task(self.worker(file))
                    for _ in range(self.cfg.concurrent_connections)
                ]

                await asyncio.gather(
                    self.producer(),
                    self.stats(),
                    *workers
                )
        finally:
            await self.client.close()


# ================= MAIN =================

async def main():
    cfg = Config()
    engine = Engine(cfg)
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())