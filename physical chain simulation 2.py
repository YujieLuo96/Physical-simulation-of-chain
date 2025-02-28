import pygame
import numpy as np
import math

# 初始化 pygame
pygame.init()

# 屏幕尺寸
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("链条物理模拟")

# 颜色
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
CHAIN_COLOR = (200, 200, 200)

# 物理参数
GRAVITY = 0.5  # 重力加速度
DAMPING = 0.98  # 阻尼系数
ITERATIONS = 10  # 约束求解迭代次数
CHAIN_SEGMENTS = 20  # 链条段数
SEGMENT_LENGTH = 15  # 每段长度


class Point:
    """质点类，表示链条中的每个节点"""

    def __init__(self, x, y, fixed=False):
        self.pos = np.array([x, y], dtype=float)
        self.prev_pos = np.array([x, y], dtype=float)
        self.fixed = fixed

    def update(self):
        """更新质点位置（应用重力和速度）"""
        if not self.fixed:
            # 保存当前位置
            temp = np.copy(self.pos)

            # Verlet 积分计算新位置
            vel = (self.pos - self.prev_pos) * DAMPING
            self.pos += vel

            # 应用重力
            self.pos[1] += GRAVITY

            # 保存前一位置
            self.prev_pos = temp

    def constrain(self, width, height):
        """限制质点在屏幕边界内"""
        if not self.fixed:
            # 屏幕边界检查
            if self.pos[0] < 0:
                self.pos[0] = 0
            elif self.pos[0] > width:
                self.pos[0] = width

            if self.pos[1] < 0:
                self.pos[1] = 0
            elif self.pos[1] > height:
                self.pos[1] = height


class Constraint:
    """约束类，用于保持两个质点之间的固定距离"""

    def __init__(self, p1, p2, length):
        self.p1 = p1
        self.p2 = p2
        self.length = length

    def solve(self):
        """解决约束，调整两个质点的位置以维持固定距离"""
        # 从 p1 到 p2 的向量
        diff = self.p2.pos - self.p1.pos

        # 当前距离
        dist = np.linalg.norm(diff)

        # 如果两点在完全相同的位置，稍微移动它们
        if dist == 0:
            dist = 0.001

        # 差异比率
        diff_factor = (self.length - dist) / dist / 2

        # 方向向量
        direction = diff * diff_factor

        # 移动非固定的点
        if not self.p1.fixed:
            self.p1.pos -= direction
        if not self.p2.fixed:
            self.p2.pos += direction


class Chain:
    """链条类，管理所有质点和约束"""

    def __init__(self, start_x, start_y, segments, segment_length):
        self.points = []
        self.constraints = []

        # 创建链条质点
        for i in range(segments + 1):
            # 第一个点是固定的
            fixed = (i == 0)
            point = Point(start_x, start_y + i * segment_length, fixed)
            self.points.append(point)

        # 创建相邻质点之间的约束
        for i in range(segments):
            constraint = Constraint(self.points[i], self.points[i + 1], segment_length)
            self.constraints.append(constraint)

    def update(self):
        """更新链条物理状态"""
        # 更新所有质点
        for point in self.points:
            point.update()

        # 多次求解约束以提高稳定性
        for _ in range(ITERATIONS):
            for constraint in self.constraints:
                constraint.solve()

        # 限制质点在屏幕边界内
        for point in self.points:
            point.constrain(WIDTH, HEIGHT)

    def draw(self, surface):
        """绘制链条"""
        # 绘制约束（链条连接）
        for constraint in self.constraints:
            p1_pos = tuple(map(int, constraint.p1.pos))
            p2_pos = tuple(map(int, constraint.p2.pos))

            # 绘制链条主线
            pygame.draw.line(surface, CHAIN_COLOR, p1_pos, p2_pos, 4)

            # 在中点绘制小圆，使链条看起来更像链接
            mid_x = (p1_pos[0] + p2_pos[0]) // 2
            mid_y = (p1_pos[1] + p2_pos[1]) // 2
            pygame.draw.circle(surface, WHITE, (mid_x, mid_y), 3)

        # 绘制连接点
        for point in self.points:
            pos = tuple(map(int, point.pos))
            color = GRAY if point.fixed else WHITE
            pygame.draw.circle(surface, color, pos, 5)


def main():
    """主函数"""
    # 创建链条
    chain = Chain(WIDTH // 2, 50, CHAIN_SEGMENTS, SEGMENT_LENGTH)

    # 鼠标交互变量
    dragged_point = None

    # 游戏循环
    running = True
    clock = pygame.time.Clock()

    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # 鼠标按下 - 尝试抓取一个点
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    mouse_pos = np.array(pygame.mouse.get_pos())

                    # 寻找最近的点
                    min_dist = float('inf')
                    closest_point = None
                    for point in chain.points:
                        dist = np.linalg.norm(point.pos - mouse_pos)
                        if dist < min_dist and dist < 20:  # 20px 抓取半径
                            min_dist = dist
                            closest_point = point

                    # 暂时固定被拖拽的点
                    if closest_point:
                        dragged_point = closest_point
                        dragged_point.fixed = True

            # 鼠标释放 - 释放任何被拖拽的点
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragged_point:
                    # 重置固定状态（除非它本来就是固定的）
                    if dragged_point != chain.points[0]:
                        dragged_point.fixed = False
                    dragged_point = None

        # 如果正在拖拽一个点，更新其位置至鼠标位置
        if dragged_point:
            mouse_pos = pygame.mouse.get_pos()
            dragged_point.pos[0] = mouse_pos[0]
            dragged_point.pos[1] = mouse_pos[1]

        # 更新物理
        chain.update()

        # 绘制
        screen.fill(BLACK)
        chain.draw(screen)
        pygame.display.flip()

        # 限制为 60 FPS
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()