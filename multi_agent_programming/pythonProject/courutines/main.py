import time

def say_after1():
    while True:
        print("kk")
        time.sleep(1)

def say_after2():
    while True:
        print("pp")
        time.sleep(1)

def main():
    say_after1()
    say_after2()

main()