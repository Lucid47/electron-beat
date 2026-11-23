from dataclasses import dataclass, field
from math import ceil
from time import monotonic_ns

SHELL_NAMES = ["K", "L"]


@dataclass(frozen=True)
class Stage:
    number: int
    symbol: str
    name: str
    shells: tuple[int, ...]
    configuration: str

    @property
    def targets(self):
        return [shell for shell, count in enumerate(self.shells) for _ in range(count)]

    @property
    def shell_summary(self):
        return " · ".join(
            f"{name} 껍질 {count}개" for name, count in zip(SHELL_NAMES, self.shells)
        )


STAGES = [
    Stage(1, "H", "수소", (1,), "1s¹"),
    Stage(2, "He", "헬륨", (2,), "1s²"),
    Stage(3, "Li", "리튬", (2, 1), "1s² 2s¹"),
    Stage(4, "Be", "베릴륨", (2, 2), "1s² 2s²"),
    Stage(5, "B", "붕소", (2, 3), "1s² 2s² 2p¹"),
    Stage(6, "C", "탄소", (2, 4), "1s² 2s² 2p²"),
    Stage(7, "N", "질소", (2, 5), "1s² 2s² 2p³"),
    Stage(8, "O", "산소", (2, 6), "1s² 2s² 2p⁴"),
    Stage(9, "F", "플루오린", (2, 7), "1s² 2s² 2p⁵"),
    Stage(10, "Ne", "네온", (2, 8), "1s² 2s² 2p⁶"),
]

TIMING_GRADES = [("PERFECT", 100), ("GREAT", 70), ("GOOD", 40)]


@dataclass(frozen=True)
class Difficulty:
    bpm: int
    travel_ms: int
    windows_ms: tuple[int, int, int]

    @property
    def capture_window_ms(self):
        return self.windows_ms[-1]


DIFFICULTIES = {
    "연습": Difficulty(72, 2000, (150, 325, 550)),
    "보통": Difficulty(120, 1700, (100, 200, 350)),
}


def clock_ms():
    return monotonic_ns() // 1_000_000


def judge_timing(error_ms, difficulty):
    for limit, (label, points) in zip(difficulty.windows_ms, TIMING_GRADES):
        if abs(error_ms) <= limit:
            return label, points
    return "MISS", 0


@dataclass
class Game:
    stage: Stage
    difficulty: Difficulty
    started_at: int
    captured: list[int] = field(default_factory=list)
    score: int = 0
    combo: int = 0
    misses: int = 0
    feedback: str = ""
    hit_at: int = field(init=False)

    def __post_init__(self):
        self.schedule(self.started_at + self.difficulty.travel_ms + 300)

    @property
    def complete(self):
        return len(self.captured) == self.stage.number

    @property
    def target(self):
        return None if self.complete else self.stage.targets[len(self.captured)]

    @property
    def spawn_at(self):
        return self.hit_at - self.difficulty.travel_ms

    def in_capture_window(self, now):
        return abs(now - self.hit_at) <= self.difficulty.capture_window_ms

    def schedule(self, earliest_hit):
        beat_ms = 60_000 / self.difficulty.bpm
        beat = ceil((earliest_hit - self.started_at) / beat_ms)
        self.hit_at = self.started_at + round(beat * beat_ms)

    def advance(self, now):
        if not self.complete and now > self.hit_at + self.difficulty.capture_window_ms:
            self.resolve(now, "MISS", 0)

    def capture(self, now):
        if self.complete or now < self.spawn_at:
            return
        error_ms = now - self.hit_at
        if error_ms < -self.difficulty.capture_window_ms:
            self.feedback = "조금 일러요. 노란 구간에서 다시 눌러보세요."
            return
        label, points = judge_timing(error_ms, self.difficulty)
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
            self.schedule(now + self.difficulty.travel_ms + 350)
