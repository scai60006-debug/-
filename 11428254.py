import turtle
import random
import time

# 顏色工具：hex <-> rgb 與插值
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*[max(0, min(255, int(v))) for v in rgb]) 


def interpolate_color(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))


# 柔和色系調色盤（較亮、偏淺的顏色）
PALETTE = ['#E6F7FF', '#FFF4E6', '#F7E6FF', '#E8FFF1', '#FFF0F6', '#E8F2FF']


def setup_screen(width=800, height=600):
    screen = turtle.Screen()
    screen.setup(width, height)
    screen.title('星空與流星 - Turtle 療癒動畫')
    screen.bgcolor('black')
    # 使用手動更新以方便控制動畫
    screen.tracer(0, 0)
    return screen


def draw_stars(screen, min_stars=100, max_stars=150):
    star_t = turtle.Turtle()
    star_t.hideturtle()
    star_t.penup()
    star_t.speed(0)

    n = random.randint(min_stars, max_stars)
    w, h = screen.window_width() // 2, screen.window_height() // 2

    stars = []
    for _ in range(n):
        x = random.randint(-w + 10, w - 10)
        y = random.randint(-h + 10, h - 10)
        # 上下翻轉：反向 y，左右翻轉：反向 x
        x = -x
        y = -y
        size = random.choice([1, 2, 3])
        color_choice = random.choices(['white'] + PALETTE, weights=[60] + [8]*len(PALETTE))[0]
        star_t.goto(x, y)
        star_t.dot(size, color_choice)
        stars.append({'x': x, 'y': y, 'size': size, 'color': color_choice, 'flicker': 0})

    screen.update()
    return star_t, stars


def draw_meteor_lines(screen, turt, start_pos, angle, length=30, step_len=20):
    # 使用單支 turtle 畫線段（線條尾巴），turt 必須為隱藏狀態
    turt.penup()
    turt.goto(start_pos)
    turt.setheading(angle)
    turt.pendown()

    head_hex = random.choice(PALETTE + ['#A7FFFC', '#FFF9C4'])
    head_rgb = hex_to_rgb(head_hex)
    end_rgb = (0, 0, 0)

    turt.pensize(2)
    for i in range(length):
        t = i / max(1, length - 1)
        c_rgb = interpolate_color(head_rgb, end_rgb, t**1.3)
        turt.pencolor(rgb_to_hex(c_rgb))
        turt.forward(step_len)
        screen.update()
        time.sleep(0.01 + random.uniform(0, 0.01))

    # 頭部小亮點
    turt.penup()
    turt.backward(step_len)
    turt.pendown()
    turt.dot(4, rgb_to_hex(head_rgb))


def main():
    screen = setup_screen(800, 600)
    # 畫星空背景並保留星星資訊
    star_t, stars = draw_stars(screen, 100, 150)

    # 準備多支用來畫線條流星的 turtle（允許同時多條線出現）
    meteor_pool = []
    pool_size = 6
    for _ in range(pool_size):
        mt = turtle.Turtle()
        mt.hideturtle()
        mt.speed(0)
        mt.penup()
        meteor_pool.append(mt)

    # 建立多個流星任務，每個任務有延遲與參數，frame-driven 更新
    num_tasks = random.randint(8, 16)
    w, h = screen.window_width() // 2, screen.window_height() // 2
    tasks = []
    for _ in range(num_tasks):
        # 起點改為左上方（x 負，y 正）
        start_x = random.randint(-w + 20, -60)
        start_y = random.randint(h // 4, h - 20)
        # 基本角度改為 315 度（右下方），使流星從左上往右下移動
        base_angle = 315
        angle = base_angle + random.uniform(-14, 14)
        length = random.randint(18, 40)
        step_len = random.randint(10, 24)
        delay_frames = random.randint(0, 40)  # frames to wait before starting
        # 每顆流星固定一個顏色，包含白色以增強亮度
        head_hex = random.choice(PALETTE + ['#A7FFFC', '#FFF9C4', 'white'])
        head_rgb = hex_to_rgb(head_hex)
        tasks.append({'start': (start_x, start_y), 'angle': angle, 'length': length, 'step': step_len, 'delay': delay_frames, 'progress': 0, 'active': False, 'turtle': None, 'color_rgb': head_rgb})

    # star flicker state
    flicker_chance = 0.02
    flicker_duration = 3

    # 主動畫迴圈：直到所有任務完成
    active_any = True
    frame_sleep = 0.03
    while True:
        all_done = True
        # 隨機讓一些星星閃爍
        for si, s in enumerate(stars):
            if s['flicker'] > 0:
                # 在閃爍期間畫成白色
                star_t.goto(s['x'], s['y'])
                star_t.dot(s['size'] + 1, 'white')
                s['flicker'] -= 1
            else:
                # 有小機率啟動閃爍
                if random.random() < flicker_chance:
                    s['flicker'] = random.randint(1, flicker_duration)
                    star_t.goto(s['x'], s['y'])
                    star_t.dot(s['size'] + 1, 'white')

        # 更新每個流星任務
        for task in tasks:
            if task['delay'] > 0:
                task['delay'] -= 1
                all_done = False
                continue

            if task['progress'] >= task['length']:
                continue

            all_done = False
            # 取得一支空閒的 turtle
            if task['turtle'] is None:
                for mt in meteor_pool:
                    if not getattr(mt, 'busy', False):
                        task['turtle'] = mt
                        mt.busy = True
                        mt.clear()
                        mt.penup()
                        mt.goto(task['start'])
                        mt.setheading(task['angle'])
                        mt.pendown()
                        break

            mt = task['turtle']
            if mt is None:
                # no available turtle this frame
                continue

            i = task['progress']
            t = i / max(1, task['length'] - 1)
            # 使用任務的固定顏色
            head_rgb = task.get('color_rgb', (167, 255, 252))
            # 由細到粗：讓筆寬隨 t 增加，頭部在 t ~ 1
            base_c = interpolate_color(head_rgb, (0, 0, 0), (1 - t)**1.3)
            if t > 0.75:
                mix = (t - 0.75) / 0.25
                base_c = interpolate_color(base_c, (255, 255, 255), 0.6 * mix)
            mt.pencolor(rgb_to_hex(base_c))
            # 讓尾部在開始時較細，接近頭部變粗
            mt.pensize(max(1, int(6 * t)))
            mt.forward(task['step'])
            task['progress'] += 1

            # 若完成，保留頭部亮點並釋放 turtle
            if task['progress'] >= task['length']:
                mt.penup()
                mt.backward(task['step'])
                mt.pendown()
                mt.dot(6, rgb_to_hex(head_rgb))
                mt.busy = False

        screen.update()
        time.sleep(frame_sleep)

        if all_done:
            break

    # 動畫結束後保留最後畫面，交由使用者關閉
    screen.update()
    turtle.done()

    # 動畫結束後保留最後畫面，交由使用者關閉
    screen.update()
    turtle.done()


if __name__ == '__main__':
    main()
