"""
Catch the Stars - простая аркадная игра на Kivy
Лови падающие звёзды корзинкой, не пропускай их!
"""

import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, Triangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector


class Star:
    """Одна падающая звезда"""

    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

    def move(self, dt):
        self.y -= self.speed * dt

    def collides_with_basket(self, basket_x, basket_y, basket_w, basket_h):
        return (
            basket_x < self.x < basket_x + basket_w
            and basket_y < self.y + self.size < basket_y + basket_h
        )


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.score = 0
        self.lives = 3
        self.game_over = False

        self.basket_w = 140
        self.basket_h = 40
        self.basket_x = Window.width / 2 - self.basket_w / 2
        self.basket_y = 30

        self.stars = []
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.difficulty_timer = 0

        # UI
        self.score_label = Label(
            text="Счёт: 0",
            font_size=28,
            pos=(10, Window.height - 50),
            size_hint=(None, None),
            halign="left",
        )
        self.lives_label = Label(
            text="Жизни: 3",
            font_size=28,
            pos=(Window.width - 180, Window.height - 50),
            size_hint=(None, None),
        )
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)

        self.game_over_label = Label(
            text="",
            font_size=40,
            center=(Window.width / 2, Window.height / 2),
            size_hint=(None, None),
        )
        self.add_widget(self.game_over_label)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    # ---------- ввод ----------
    def on_touch_move(self, touch):
        self._move_basket_to(touch.x)

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart()
        else:
            self._move_basket_to(touch.x)

    def _move_basket_to(self, x):
        self.basket_x = max(0, min(Window.width - self.basket_w, x - self.basket_w / 2))

    # ---------- логика ----------
    def spawn_star(self):
        x = random.uniform(20, Window.width - 20)
        size = random.uniform(20, 35)
        speed = random.uniform(150, 250) + self.score * 2
        self.stars.append(Star(x, Window.height, size, speed))

    def restart(self):
        self.score = 0
        self.lives = 3
        self.stars = []
        self.game_over = False
        self.spawn_interval = 1.0
        self.game_over_label.text = ""
        self.update_labels()

    def update_labels(self):
        self.score_label.text = f"Счёт: {self.score}"
        self.lives_label.text = f"Жизни: {self.lives}"

    def update(self, dt):
        if self.game_over:
            self.draw()
            return

        # спавн новых звёзд
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_star()

        # со временем игра ускоряется
        self.difficulty_timer += dt
        if self.difficulty_timer > 5:
            self.difficulty_timer = 0
            self.spawn_interval = max(0.35, self.spawn_interval - 0.08)

        # движение звёзд
        for star in self.stars[:]:
            star.move(dt)

            if star.collides_with_basket(
                self.basket_x, self.basket_y, self.basket_w, self.basket_h
            ):
                self.stars.remove(star)
                self.score += 1
                self.update_labels()
                continue

            if star.y < -star.size:
                self.stars.remove(star)
                self.lives -= 1
                self.update_labels()
                if self.lives <= 0:
                    self.game_over = True
                    self.game_over_label.text = (
                        f"Игра окончена!\nСчёт: {self.score}\nТапни, чтобы начать снова"
                    )

        self.draw()

    # ---------- отрисовка ----------
    def draw(self):
        self.canvas.before.clear()
        with self.canvas.before:
            # фон
            Color(0.05, 0.05, 0.2, 1)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # звёзды
            Color(1, 0.85, 0.2, 1)
            for star in self.stars:
                Ellipse(pos=(star.x - star.size / 2, star.y - star.size / 2),
                         size=(star.size, star.size))

            # корзинка
            Color(0.3, 0.7, 1, 1)
            Rectangle(
                pos=(self.basket_x, self.basket_y),
                size=(self.basket_w, self.basket_h),
            )


class CatchStarsApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.2, 1)
        return GameWidget()


if __name__ == "__main__":
    CatchStarsApp().run()
