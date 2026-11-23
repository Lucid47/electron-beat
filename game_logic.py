from dataclasses import dataclass, field
from math import ceil
from time import monotonic_ns

SHELLS = [("K", 2), ("L", 1)]
TARGETS = [index for index, (_, count) in enumerate(SHELLS) for _ in range(count)]

# (maximum absolute timing error in milliseconds, label, base points)
TIMING = [(60, "PERFECT", 100), (120, "GREAT", 70), (200, "GOOD", 40)]
MISS_WINDOW = TIMING[-1][0]
TEMPOS = {"연습": (72, 2000), "보통": (120, 1400)}


def clock_ms():
    return monotonic_ns() // 1_000_000


def judge_timing(error_ms):
    for limit, label, points in TIMING:
        if abs(error_ms) <= limit:
            return label, points
    return "MISS", 0


@dataclass
class Game:
    bpm: int
    travel_ms: int
    started_at: int
    captured: list[int] = field(default_factory=list)
    score: int = 0
    combo: int = 0
    misses: int = 0
    feedback: str = ""
    hit_at: int = field(init=False)

    def __post_init__(self):
        self.schedule(self.started_at + self.travel_ms + 300)

    @property
    def complete(self):
        return len(self.captured) == len(TARGETS)

    @property
    def target(self):
        return None if self.complete else TARGETS[len(self.captured)]

    @property
    def spawn_at(self):
        return self.hit_at - self.travel_ms

    def schedule(self, earliest_hit):
        beat_ms = 60_000 / self.bpm
        beat = ceil((earliest_hit - self.started_at) / beat_ms)
        self.hit_at = self.started_at + round(beat * beat_ms)

    def advance(self, now):
        if not self.complete and now > self.hit_at + MISS_WINDOW:
            self.resolve(now, "MISS", 0)

    def capture(self, now):
        if self.complete or now < self.spawn_at:
            return
        label, points = judge_timing(now - self.hit_at)
        self.resolve(now, label, points)

    def resolve(self, now, label, points):
        if points:
            self.captured.append(now)
            self.combo += 1
            gained = points + 10 * (self.combo - 1)
            self.score += gained
            self.feedback = f"{label}  +{gained}"
        else:
            self.combo = 0
            self.misses += 1
            self.feedback = "MISS  ·  같은 껍질에 다시 도전"
        if not self.complete:
            self.schedule(now + self.travel_ms + 350)
