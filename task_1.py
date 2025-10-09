import time

# ---------- Новый генератор программы робота ----------
def generate_robot_program(max_search_power=10):
    program = []
    pc = 2
    program.append("1: GOTO 1")

    def add_step(cmd: str):
        nonlocal pc
        program.append(f"{pc}: {cmd}")
        pc += 1
        program.append(f"{pc}: IF FLAG")
        pc += 1
        program.append(f"{pc}: GOTO 1")
        pc += 1

    for power in range(max_search_power):
        d = 2 ** power
        for _ in range(d): add_step("MR")
        for _ in range(d): add_step("ML")
        for _ in range(2 * d): add_step("ML")
        for _ in range(2 * d): add_step("MR")

    program.append(f"{pc}: GOTO {pc}")
    return program

# --- ИСПРАВЛЕННЫЙ КЛАСС ROBOT ---
class Robot:
    def __init__(self, position, program_map):
        self.pos = position
        self.pc = 2
        self.program = program_map
        self.is_halted = False

    def step(self, black_square_pos):
        if self.is_halted:
            return

        time_taken = 0
        while time_taken == 0:
            if self.is_halted: # <-- ВОТ ОН, ФИКС
                return

            if self.pc not in self.program:
                print(f"Error: PC {self.pc} out of bounds!")
                self.is_halted = True
                return

            cmd, *args = self.program[self.pc]

            if cmd == "ML":
                self.pos -= 1; self.pc += 1; time_taken = 1
            elif cmd == "MR":
                self.pos += 1; self.pc += 1; time_taken = 1
            elif cmd == "IF":
                self.pc += 1 if self.pos == black_square_pos else 2
                time_taken = 1
            elif cmd == "GOTO":
                target_pc = int(args[0])
                if target_pc == 1:
                    self.is_halted = True
                self.pc = target_pc
                time_taken = 0

class World:
    # ... (остальной код без изменений) ...
    def __init__(self, robot1_pos, robot2_pos, black_square_pos, program):
        self.program_map = self._parse_program(program)
        self.r1 = Robot(robot1_pos, self.program_map)
        self.r2 = Robot(robot2_pos, self.program_map)
        self.black_square = black_square_pos
        self.time = 0

    def _parse_program(self, program_text):
        parsed = {}
        for line in program_text:
            num, cmd_str = line.split(":", 1)
            parsed[int(num)] = cmd_str.strip().split()
        return parsed

    def run_simulation(self, max_time=2000, verbose=True):
        print(f"Старт. R1: {self.r1.pos}, R2: {self.r2.pos}, Флаг: {self.black_square}")
        print("-" * 60)

        while self.r1.pos != self.r2.pos:
            if self.time > max_time:
                print("Симуляция прервана по таймауту.")
                return

            self.r1.step(self.black_square)
            self.r2.step(self.black_square)
            self.time += 1

            if verbose:
                s1 = "ЗАСТЫЛ" if self.r1.is_halted else f"ищет (PC:{self.r1.pc})"
                s2 = "ЗАСТЫЛ" if self.r2.is_halted else f"ищет (PC:{self.r2.pc})"
                print(f"t={self.time:4}s | R1:{self.r1.pos:4} {s1} | "
                      f"R2:{self.r2.pos:4} {s2}")
                time.sleep(0.03)

        print("-" * 60)
        print(f"Встреча! Клетка {self.r1.pos}, время {self.time} c.")

# ---------- Запуск ----------
generated_program = generate_robot_program(max_search_power=8)
world = World(robot1_pos=-7, robot2_pos=12, black_square_pos=0, program=generated_program)
world.run_simulation()
