"""
Flask app to create a favicon with custom text and colors.

"""

from dataclasses import dataclass
from io import BytesIO

from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)


@dataclass
class FaviconConfig:
    """Configuration for the favicon image"""

    text: str
    text_color: str
    background_color: str
    favicon_dim: int = 16
    text_to_image_ratio: float = 2 / 3
    high_rez_scale_factor: int = 3


def create_image(config: FaviconConfig, image_size: tuple[int, int]) -> Image.Image:
    """Create an image with the given text and colors."""
    high_res_image = Image.new("RGBA", image_size, config.background_color)
    draw = ImageDraw.Draw(high_res_image)

    font_size = int(image_size[0] * config.text_to_image_ratio)

    font = ImageFont.load_default(size=font_size)

    x = image_size[0] // 2
    y = image_size[1] // 2

    draw.text((x, y), config.text, font=font, fill=config.text_color, anchor="mm")

    return high_res_image


def create_favicon_image(
    text: str, text_color: str, background_color: str, favicon_dim: int
) -> BytesIO:
    """Create a favicon image with the given text, colors, and size."""
    config = FaviconConfig(
        text=text,
        text_color=text_color,
        background_color=background_color,
        favicon_dim=favicon_dim,
    )

    high_res_dim = config.favicon_dim * 2**config.high_rez_scale_factor
    high_res_image = create_image(config, (high_res_dim, high_res_dim))
    favicon_image = high_res_image.resize((config.favicon_dim, config.favicon_dim), resample=1)

    image_bytes = BytesIO()
    favicon_image.save(image_bytes, format="ICO")
    image_bytes.seek(0)

    return image_bytes


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the index page and handle the favicon creation."""
    if request.method == "POST":
        text = request.form.get("text", "F")
        text_color = request.form.get("text_color", "white")
        background_color = request.form.get("background_color", "black")
        favicon_dim = int(request.form.get("favicon_size", 16))

        image_bytes = create_favicon_image(text, text_color, background_color, favicon_dim)

        return send_file(
            image_bytes, mimetype="image/x-icon", as_attachment=True, download_name="favicon.ico"
        )
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
