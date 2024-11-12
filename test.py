from ursina import *

if __name__ == "__main__":
    app = Ursina()
    from solver import MainPage
    MainPage("R U R F' B' L' D2 R2")
    app.run()