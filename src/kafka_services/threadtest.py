import threading


def write_date_to_file(tmpfilename):
    r_counter = 0
    while True:
        my_lock.acquire()
        with open(tmpfilename, "a") as wrfile:
            r_counter = r_counter + 1
            wrfile.write("Hi .. write line - {0}\n".format(r_counter))
        my_lock.release()


def read_data_to_file(tmp_file_name):
    while True:
        my_lock.acquire()
        with open(tmp_file_name, "r") as rfile:
            line_to_read = rfile.readline()
            print("Line read :: {0}".format(line_to_read))
        my_lock.release()


if __name__ == "__main__":
    tmpfilename = "/Users/kamalsaidevarapalli/Desktop/Workshop/PyPortalAdminstration/src/kafka_services/datafile.txt"

    write_thread = threading.Thread(target=write_date_to_file, args=(tmpfilename,))
    read_thread = threading.Thread(target=read_data_to_file, args=(tmpfilename,))
    my_lock = threading.Lock()
    write_thread.start()
    read_thread.start()

    write_thread.join()
    read_thread.join()
