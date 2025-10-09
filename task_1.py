import time

# --- ПРОГРАММА ДЛЯ РОБОТОВ ---
# Логика: расширяющийся линейный поиск (1 шаг вправо, 2 влево, 3 вправо, 4 влево...)
# Как только флаг найден, робот переходит в режим "охоты" - движется только вправо.

ROBOT_PROGRAM = [
    # --- РЕЖИМ ОХОТЫ ---
    # Если робот нашел флаг, он попадает сюда и просто движется вправо.
    "1: MR",        # Сделать шаг вправо
    "2: GOTO 1",    # Повторить

    # --- РАСШИРЯЮЩИЙСЯ ПОИСК ---
    # Начало. Стартуем с первого правого шага.
    "3: GOTO 100",  # Начать с поиска 1 шага вправо

    # --- Блок поиска ВПРАВО (N шагов) ---
    # Сюда мы попадаем, чтобы сделать N шагов вправо.
    # После каждого шага - проверка флага.
    # После N шагов переходим к поиску ВЛЕВО (N+1 шаг).

    # Фаза 1: 1 шаг вправо
    "100: MR",
    "101: IF FLAG",
    "102: GOTO 1",     # Флаг найден! Включить режим охоты.
    "103: GOTO 200",   # Флаг не найден. Начать фазу 2 (2 шага влево).

    # Фаза 3: 3 шага вправо
    "104: MR",
    "105: IF FLAG",
    "106: GOTO 1",
    "107: GOTO 108",
    "108: MR",
    "109: IF FLAG",
    "110: GOTO 1",
    "111: GOTO 112",
    "112: MR",
    "113: IF FLAG",
    "114: GOTO 1",
    "115: GOTO 203",   # Начать фазу 4 (4 шага влево).


    # --- Блок поиска ВЛЕВО (N шагов) ---
    # Аналогично блоку выше, но для движения влево.

    # Фаза 2: 2 шага влево
    "200: ML",
    "201: IF FLAG",
    "202: GOTO 1",     # Флаг найден! Включить режим охоты.
    "203: GOTO 204",
    "204: ML",
    "205: IF FLAG",
    "206: GOTO 1",
    "207: GOTO 104",   # Начать фазу 3 (3 шага вправо).

    # И так далее. Программа теоретически бесконечна, но для любой конечной
    # дистанции достаточно конечного числа строк.
]


class Robot:
    def __init__(self, position, program):
        self.pos = position
        self.pc = 3  # Program counter, starts at line 3
        self.program = self._parse_program(program)

    def _parse_program(self, program_text):
        parsed = {}
        for line in program_text:
            num, cmd = line.split(":", 1)
            parsed[int(num)] = cmd.strip().split()
        return parsed

    def step(self, black_square_pos):
        time_taken = 0
        while time_taken == 0:
            cmd_parts = self.program[self.pc]
            cmd = cmd_parts[0]

            if cmd == "ML":
                self.pos -= 1
                self.pc += 1
                time_taken = 1
            elif cmd == "MR":
                self.pos += 1
                self.pc += 1
                time_taken = 1
            elif cmd == "IF": # IF FLAG
                on_flag = (self.pos == black_square_pos)
                if on_flag:
                    self.pc += 1
                else:
                    self.pc += 2
                time_taken = 1
            elif cmd == "GOTO":
                self.pc = int(cmd_parts[1])
                time_taken = 0 # GOTO is instant
        return time_taken

class World:
    def __init__(self, robot1_pos, robot2_pos, black_square_pos, program):
        self.r1 = Robot(robot1_pos, program)
        self.r2 = Robot(robot2_pos, program)
        self.black_square = black_square_pos
        self.time = 0

    def run_simulation(self, max_time=100, verbose=True):
        print(f"Старт. Робот1: {self.r1.pos}, Робот2: {self.r2.pos}, Флаг: {self.black_square}")
        print("-" * 40)

        while self.r1.pos != self.r2.pos:
            if self.time > max_time:
                print("Симуляция прервана по таймауту.")
                return

            # Роботы ходят одновременно
            self.r1.step(self.black_square)
            self.r2.step(self.black_square)
            self.time += 1 # 1 секунда на команду

            if verbose:
                print(f"Время: {self.time}с | R1_pos: {self.r1.pos} (PC:{self.r1.pc}) | R2_pos: {self.r2.pos} (PC:{self.r2.pc})")
                time.sleep(0.1)


        print("-" * 40)
        print(f"Встреча! Позиция: {self.r1.pos}. Общее время: {self.time} секунд.")


# --- ЗАПУСК ---
# Робот 1 слева от флага, Робот 2 справа.
world = World(robot1_pos=-5, robot2_pos=10, black_square_pos=0, program=ROBOT_PROGRAM)
world.run_simulation()