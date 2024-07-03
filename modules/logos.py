class Logos:
    """Caches the content of image files"""

    with open("./static/kgsmun-logo.png", "rb") as f:
        KGSMUN = f.read()
    with open("./static/facebook-logo.png", "rb") as f:
        FACEBOOK = f.read()
    with open("./static/instagram-logo.png", "rb") as f:
        INSTA = f.read()
