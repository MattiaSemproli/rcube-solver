from ursina import *

if __name__ == "__main__":
    app = Ursina()
    from solver import MainPage
    MainPage("R U R F' B' L' D2 B2 U2 L2 D2 R2 U2 F2 L2 D2 B2 U2 R2")
    app.run()