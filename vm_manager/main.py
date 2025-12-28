import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from vm_manager.gui.main_window import MainWindow

# functia principala care porneste aplicatia
def main():
    print("Starting VM Manager...")
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
