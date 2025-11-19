# ==========================================================
# run_main.py
# รวมเมนูหลักเรียกใช้ 5.1 , 5.2 , 5.3
# ==========================================================

import sys

# Import 
import analysis_5_1 as a51
import analysis_5_2 as a52
import analysis_5_3 as a53 


def main_menu():
    while True:
        print("\n==================== SME ANALYTICS MAIN MENU ====================")
        print("1) Run Task 5.1  (Basic Analysis)")
        print("2) Run Task 5.2  (Visualization / SME Structure)")
        print("3) Run Task 5.3  (Growth Gap Analysis)")
        print("0) Exit")
        print("=================================================================")

        choice = input("\nSelect your choice: ")

        if choice == "1":
            print("\n>>> Running Task 5.1 ...")
            a51.run_5_1()

        elif choice == "2":
            print("\n>>> Running Task 5.2 ...")
            a52.run_5_2()

        elif choice == "3":
            print("\n>>> Running Task 5.3 ...")
            a53.menu()     # หรือ a53.run_5_3()

        elif choice == "0":
            print("\nBye")
            sys.exit()

        else:
            print("\n❗ Invalid choice, please try again.")


if __name__ == "__main__":
    main_menu()
