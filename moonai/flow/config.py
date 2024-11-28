DARK_GRAY = "#333333"
moonai_ORANGE = "#FF5A50"
GRAY = "#666666"
WHITE = "#FFFFFF"
BLACK = "#000000"

COLORS = {
    "bg": WHITE,
    "start": moonai_ORANGE,
    "method": DARK_GRAY,
    "router": DARK_GRAY,
    "router_border": moonai_ORANGE,
    "edge": GRAY,
    "router_edge": moonai_ORANGE,
    "text": WHITE,
}

NODE_STYLES = {
    "start": {
        "color": moonai_ORANGE,
        "shape": "box",
        "font": {"color": WHITE},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "method": {
        "color": DARK_GRAY,
        "shape": "box",
        "font": {"color": WHITE},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "router": {
        "color": {
            "background": DARK_GRAY,
            "border": moonai_ORANGE,
            "highlight": {
                "border": moonai_ORANGE,
                "background": DARK_GRAY,
            },
        },
        "shape": "box",
        "font": {"color": WHITE},
        "borderWidth": 3,
        "borderWidthSelected": 4,
        "shapeProperties": {"borderDashes": [5, 5]},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "squad": {
        "color": {
            "background": WHITE,
            "border": moonai_ORANGE,
        },
        "shape": "box",
        "font": {"color": BLACK},
        "borderWidth": 3,
        "borderWidthSelected": 4,
        "shapeProperties": {"borderDashes": False},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
}
