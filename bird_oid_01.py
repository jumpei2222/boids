import pygame
from random import randint
import numpy as np
import math

#pygame用の定数
BLACK = (0,0,0)
WHITE = (255,255,255)
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500

GAME_SIZE = 60

# シミュレーションパラメタ
N = 256
# 力の強さ
COHESION_FORCE = 0.005 * GAME_SIZE
SEPARATION_FORCE = 0.5 * GAME_SIZE
ALIGNMENT_FORCE = 0.01 * GAME_SIZE
# 力の働く距離
COHESION_DISTANCE = 0.8 * GAME_SIZE
SEPARATION_DISTANCE = 0.03 * GAME_SIZE
ALIGNMENT_DISTANCE = 0.5 * GAME_SIZE
# 力の働く角度
COHESION_ANGLE = np.pi / 2
SEPARATION_ANGLE = np.pi / 2
ALIGNMENT_ANGLE = np.pi / 3
# 速度の上限/下限
MIN_VEL = 0.005 * GAME_SIZE
MAX_VEL = 0.03 * GAME_SIZE
# 境界で働く力（0にすると自由境界）
BOUNDARY_FORCE = 0.001 * GAME_SIZE
# 位置と速度
#x = np.random.rand(N, 2) * 2 - 1
v = (np.random.rand(N, 2) * 500 - 1 ) * MIN_VEL

# cohesion, separation, alignmentの３つの力を代入する変数
dv_coh = np.empty((N,2))
dv_sep = np.empty((N,2))
dv_ali = np.empty((N,2))
# 境界で働く力を代入する変数
dv_boundary = np.empty((N,2))

pygame.init()

size = (SCREEN_WIDTH,SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Boids")

playing = True

clock = pygame.time.Clock()

boid_size = 5
root_3 = 1.732

#0-1のランダムな数字をN行、2列生成
x = np.random.rand(N, 2) * 700 - 1
#boid_manager = BoidManager()

img = pygame.image.load("bird_20_20.png")

while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

    screen.fill(WHITE)

    #boid_manager.update_boids()
    for i in range(N):
        # ここで計算する個体の位置と速度
        x_this = x[i]
        v_this = v[i]
        # それ以外の個体の位置と速度の配列
        x_that = np.delete(x, i, axis=0)
        v_that = np.delete(v, i, axis=0)
        # 個体間の距離と角度
        distance = np.linalg.norm(x_that - x_this, axis=1)
        angle = np.arccos(np.dot(v_this, (x_that-x_this).T) / (np.linalg.norm(v_this) * np.linalg.norm((x_that-x_this), axis=1)))
        # 各力が働く範囲内の個体のリスト
        coh_agents_x = x_that[ (distance < COHESION_DISTANCE) & (angle < COHESION_ANGLE) ]
        sep_agents_x = x_that[ (distance < SEPARATION_DISTANCE) & (angle < SEPARATION_ANGLE) ]
        ali_agents_v = v_that[ (distance < ALIGNMENT_DISTANCE) & (angle < ALIGNMENT_ANGLE) ]
        # 各力の計算
        dv_coh[i] = COHESION_FORCE * (np.average(coh_agents_x, axis=0) - x_this) if (len(coh_agents_x) > 0) else 0
        dv_sep[i] = SEPARATION_FORCE * np.sum(x_this - sep_agents_x, axis=0) if (len(sep_agents_x) > 0) else 0
        dv_ali[i] = ALIGNMENT_FORCE * (np.average(ali_agents_v, axis=0) - v_this) if (len(ali_agents_v) > 0) else 0
        #dist_center = np.linalg.norm(x_this) # 原点からの距離
        #dv_boundary[i] = - BOUNDARY_FORCE * x_this * (dist_center - 1) / dist_center if (dist_center > 700) else 0
    # 速度のアップデートと上限/下限のチェック
    v += dv_coh + dv_sep + dv_ali
    #v += dv_coh + dv_sep + dv_ali + dv_boundary
    for i in range(N):
        v_abs = np.linalg.norm(v[i])
        if (v_abs < MIN_VEL):
            v[i] = MIN_VEL * v[i] / v_abs
        elif (v_abs > MAX_VEL):
            v[i] = MAX_VEL * v[i] / v_abs
    # 位置のアップデート
    x += v

    for i in range(N):
        if x[i][0]<0:
            x[i][0] += SCREEN_WIDTH
        elif x[i][0]>SCREEN_WIDTH:
            x[i][0] += SCREEN_WIDTH*-1
        if x[i][1] <0:
            x[i][1]+= SCREEN_HEIGHT
        elif x[i][1] > SCREEN_HEIGHT:
            x[i][1]+= SCREEN_HEIGHT*-1 
    for i in range(N):

        #pygame.draw.polygon(screen, WHITE, [[a[0], a[1]],
        #                [a[0] + boid_size, a[1] + boid_size*root_3], 
        #                [a[0] - boid_size, a[1] + boid_size*root_3]])
        r_img = pygame.transform.rotate(img,math.degrees(angle[i-1]))
        screen.blit(r_img,[x[i][0],x[i][1]])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()