# External Dependencies
from PIL import Image, ImageDraw, ImageFont
import os
import pathlib
import spidev as SPI
import time
from multiprocessing import Queue

from seedsigner.helpers import B, ST7789

### Generic View Class to Instatiate Display
### Static Class variables are used for display
### Designed to be inherited for other view classes, but not required

class View:

    WIDTH = 240
    HEIGHT = 240

    # Define necessary fonts
    IMPACT16 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 16)
    IMPACT18 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 18)
    IMPACT20 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 20)
    IMPACT21 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 21)
    IMPACT22 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 22)
    IMPACT23 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 23)
    IMPACT25 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 25)
    IMPACT26 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 26)
    IMPACT35 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 35)
    IMPACT50 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Impact.ttf', 50)
    COURIERNEW14 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/courbd.ttf', 14)
    COURIERNEW24 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/courbd.ttf', 24)
    COURIERNEW38 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/courbd.ttf', 38)
    COURIERNEW30 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/courbd.ttf', 30)
    COURIERNEW20 = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/courbd.ttf', 20)

    font_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "..", "resources", "fonts")
    print(font_path)

    ROBOTOCONDENSED24 = ImageFont.truetype(os.path.join(font_path, "RobotoCondensed-Light.ttf"), 24)

    RST = 27
    DC = 25
    BL = 24

    controller = None
    buttons = None
    canvas_width = 0
    canvas_height = 0
    canvas = None
    draw = None
    bus = 0
    device = 0
    disp = None

    def __init__(self, controller) -> None:

        # Global Singleton
        View.controller = controller
        View.buttons = View.controller.buttons
        View.color = View.controller.color

        View.canvas_width = View.WIDTH
        View.canvas_height = View.HEIGHT
        View.canvas = Image.new('RGB', (View.canvas_width, View.canvas_height))
        View.draw = ImageDraw.Draw(View.canvas)

        # 240x240 display with hardware SPI:
        View.bus = 0
        View.device = 0
        View.disp = ST7789(SPI.SpiDev(View.bus, View.device),View.RST, View.DC, View.BL)
        View.disp.Init()

        self.queue = Queue()

    def DispShowImage(image=None, alpha_overlay=None):
        if image == None:
            image = View.canvas
        if alpha_overlay:
            image = Image.alpha_composite(image, alpha_overlay)
        View.disp.ShowImage(image, 0, 0)

    def disp_show_image_pan(image, start_x, start_y, end_x, end_y, rate, alpha_overlay=None):
        cur_x = start_x
        cur_y = start_y
        rate_x = rate
        rate_y = rate
        if end_x - start_x < 0:
            rate_x = rate_x * -1
        if end_y - start_y < 0:
            rate_y = rate_y * -1

        while (cur_x != end_x or cur_y != end_y) and (rate_x != 0 or rate_y != 0):
            cur_x += rate_x
            if (rate_x > 0 and cur_x > end_x) or (rate_x < 0 and cur_x < end_x):
                cur_x -= rate_x
                rate_x = 0

            cur_y += rate_y
            if (rate_y > 0 and cur_y > end_y) or (rate_y < 0 and cur_y < end_y):
                cur_y -= rate_y
                rate_y = 0

            crop = image.crop((cur_x, cur_y, cur_x + View.canvas_width, cur_y + View.canvas_height))

            if alpha_overlay:
                crop = Image.alpha_composite(crop, alpha_overlay)

            View.disp.ShowImage(crop, 0, 0)



    def DispShowImageWithText(image, text, font=None, text_color="GREY", text_background=None):
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy)
        if not font:
            font = View.COURIERNEW14
        tw, th = draw.textsize(text, font=font)
        if text_background:
            draw.rectangle(((240 - tw) / 2 - 3, 240 - th, (240 - tw) / 2 + tw + 3, 240), fill=text_background)
        draw.text(((240 - tw) / 2, 240 - th - 1), text, fill=text_color, font=font)
        View.disp.ShowImage(image_copy, 0, 0)


    def draw_modal(self, lines = [], title = "", bottom = "") -> None:
        View.draw.rectangle((0, 0, View.canvas_width, View.canvas_height), outline=0, fill=0)

        if len(title) > 0:
            tw, th = View.draw.textsize(title, font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 2), title, fill=View.color, font=View.IMPACT22)

        if len(bottom) > 0:
            tw, th = View.draw.textsize(bottom, font=View.IMPACT18)
            View.draw.text(((240 - tw) / 2, 210), bottom, fill=View.color, font=View.IMPACT18)

        if len(lines) == 1:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT26)
            View.draw.text(((240 - tw) / 2, 90), lines[0], fill=View.color, font=View.IMPACT26)
        elif len(lines) == 2:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[0], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[1], fill=View.color, font=View.IMPACT22)
        elif len(lines) == 3:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT26)
            View.draw.text(((240 - tw) / 2, 55), lines[0], fill=View.color, font=View.IMPACT26)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[1], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[2], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[2], fill=View.color, font=View.IMPACT22)
        elif len(lines) == 4:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 55), lines[0], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[1], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[2], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[2], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[3], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 160), lines[3], fill=View.color, font=View.IMPACT22)

        View.DispShowImage()

        return

    def draw_prompt_yes_no(self, lines = [], title = "", bottom = "") -> None:

        self.draw_prompt_custom("", "Yes ", "No ", lines, title, bottom)
        return

    def draw_prompt_custom(self, a_txt, b_txt, c_txt, lines = [], title = "", bottom = "") -> None:

        View.draw.rectangle((0, 0, View.canvas_width, View.canvas_height), outline=0, fill=0)

        if len(title) > 0:
            tw, th = View.draw.textsize(title, font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 2), title, fill=View.color, font=View.IMPACT22)

        if len(bottom) > 0:
            tw, th = View.draw.textsize(bottom, font=View.IMPACT18)
            View.draw.text(((240 - tw) / 2, 210), bottom, fill=View.color, font=View.IMPACT18)

        if len(lines) == 1:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT26)
            View.draw.text(((240 - tw) / 2, 90), lines[0], fill=View.color, font=View.IMPACT26)
        elif len(lines) == 2:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[0], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[1], fill=View.color, font=View.IMPACT22)
        elif len(lines) == 3:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT26)
            View.draw.text(((240 - tw) / 2, 20), lines[0], fill=View.color, font=View.IMPACT26)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[1], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[2], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[2], fill=View.color, font=View.IMPACT22)
        elif len(lines) == 4:
            tw, th = View.draw.textsize(lines[0], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 20), lines[0], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[1], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 90), lines[1], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[2], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 125), lines[2], fill=View.color, font=View.IMPACT22)
            tw, th = View.draw.textsize(lines[3], font=View.IMPACT22)
            View.draw.text(((240 - tw) / 2, 160), lines[3], fill=View.color, font=View.IMPACT22)

        a_x_offset = 240 - View.IMPACT25.getsize(a_txt)[0]
        View.draw.text((a_x_offset, 39 + 0), a_txt, fill=View.color, font=View.IMPACT25)

        b_x_offset = 240 - View.IMPACT25.getsize(b_txt)[0]
        View.draw.text((b_x_offset , 39 + 60), b_txt, fill=View.color, font=View.IMPACT25)

        c_x_offset = 240 - View.IMPACT25.getsize(c_txt)[0]
        View.draw.text((c_x_offset , 39 + 120), c_txt, fill=View.color, font=View.IMPACT25)

        View.DispShowImage()

        return


    def display_qwerty(self):
        lines = [
            "1234567890",
            "abcdefghij",
            "klmnopqrst",
            "uvwxyz"
        ]

        y_start = 60
        cur_y = y_start
        y_height = 34
        y_gap = 6
        x_width = 22
        x_gap = 1

        # Set up the blank keyboard first
        View.draw.rectangle((0, 0, View.canvas_width, View.canvas_height), outline=0, fill=0)

        for line in lines:
            cur_x = 0
            for letter in line:
                tw, th = View.draw.textsize(letter, font=View.ROBOTOCONDENSED24)
                View.draw.text((cur_x + int((x_width - tw) / 2), cur_y + int((y_height - th)/2)), letter, fill=View.color, font=View.ROBOTOCONDENSED24)
                View.draw.rectangle((cur_x, cur_y, cur_x + x_width, cur_y + y_height), outline="#333")
                cur_x += x_width + x_gap
            cur_y += y_height + y_gap

        View.DispShowImage()

        selected = {"x": 0, "y": 1}  # col 0, row 1: "a"
        while True:
            # Render the selected letter
            cur_x = selected["x"] * (x_width + x_gap)
            cur_y = y_start + (selected["y"] * (y_height + y_gap))
            letter = lines[selected["y"]][selected["x"]]
            View.draw.rectangle((cur_x, cur_y, cur_x + x_width, cur_y + y_height), fill=View.color)
            tw, th = View.draw.textsize(letter, font=View.ROBOTOCONDENSED24)
            View.draw.text((cur_x + int((x_width - tw) / 2), cur_y + int((y_height - th)/2)), letter, fill="BLACK", font=View.ROBOTOCONDENSED24)
            View.DispShowImage()

            # Joystick is too responsive with check_release=False; slow down our input rate
            time.sleep(0.03)

            input = self.buttons.wait_for([B.KEY_UP, B.KEY_DOWN, B.KEY_LEFT, B.KEY_RIGHT, B.KEY_PRESS], check_release=False)

            if input == B.KEY_RIGHT:
                selected["x"] += 1
                if selected["x"] == len(lines[selected["y"]]):
                    # Loop it back to the right side
                    selected["x"] = 0

            elif input == B.KEY_LEFT:
                selected["x"] -= 1
                if selected["x"] < 0:
                    # Loop it back to the left side
                    selected["x"] = len(lines[selected["y"]]) - 1

            elif input == B.KEY_DOWN:
                selected["y"] += 1
                if selected["y"] == len(lines):
                    # Loop it back to the top
                    selected["y"] = 0
                if selected["x"] >= len(lines[selected["y"]]):
                    # This line is too short to land here
                    selected["y"] = 0

            elif input == B.KEY_UP:
                selected["y"] -= 1
                if selected["y"] < 0:
                    # Loop it back to the bottom
                    selected["y"] = len(lines) - 1
                if selected["x"] >= len(lines[selected["y"]]):
                    # This line is too short to land here
                    selected["y"] -= 1

            # Before we render the next frame, undo our selected letter
            View.draw.rectangle((cur_x, cur_y, cur_x + x_width, cur_y + y_height), fill=0)
            tw, th = View.draw.textsize(letter, font=View.ROBOTOCONDENSED24)
            View.draw.text((cur_x + int((x_width - tw) / 2), cur_y + int((y_height - th)/2)), letter, fill=View.color, font=View.ROBOTOCONDENSED24)
            View.draw.rectangle((cur_x, cur_y, cur_x + x_width, cur_y + y_height), outline="#333")

        return
        

    ###
    ### Power Off Screen
    ###

    def display_power_off_screen(self):

        View.draw.rectangle((0, 0, View.canvas_width, View.canvas_height), outline=0, fill=0)

        line1 = "Powering Down..."
        line2 = "Please wait about"
        line3 = "30 seconds before"
        line4 = "disconnecting power."

        tw, th = View.draw.textsize(line1, font=View.IMPACT22)
        View.draw.text(((240-tw)/2, 45), line1, fill=View.color, font=View.IMPACT22)
        tw, th = View.draw.textsize(line2, font=View.IMPACT20)
        View.draw.text(((240-tw)/2, 100), line2, fill=View.color, font=View.IMPACT20)
        tw, th = View.draw.textsize(line3, font=View.IMPACT20)
        View.draw.text(((240-tw)/2, 130), line3, fill=View.color, font=View.IMPACT20)
        tw, th = View.draw.textsize(line4, font=View.IMPACT20)
        View.draw.text(((240-tw)/2, 160), line4, fill=View.color, font=View.IMPACT20)
        View.DispShowImage()


    def display_blank_screen(self):
        View.draw.rectangle((0, 0, View.canvas_width, View.canvas_height), outline=0, fill=0)
        View.DispShowImage()
