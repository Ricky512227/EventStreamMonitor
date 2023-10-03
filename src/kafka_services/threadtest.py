import threading


def writedattofile(tmpfilename):
    rcounter = 0
    while True:
        mylock.acquire()
        with open(tmpfilename, "a") as wfile:
            rcounter = rcounter + 1
            wfile.write("Hi .. write line - {0}\n".format(rcounter))
        mylock.release()


def readdattofile(tmpfilename):
    while True:
        mylock.acquire()
        with open(tmpfilename, "r") as rfile:
            rfile.seek(0, 2)
            linetoread = rfile.readline()
            print("Line readed :: {0}".format(linetoread))
        mylock.release()


if __name__ == "__main__":
    tmpfilename = "/Users/kamalsaidevarapalli/Desktop/Workshop/PyPortalAdminstration/src/kafka_services/datafile.txt"

    t1 = threading.Thread(target=writedattofile, args=(tmpfilename,))
    t2 = threading.Thread(target=readdattofile, args=(tmpfilename,))
    mylock = threading.Lock()
    t1.start()
    t2.start()

    t1.join()
    t2.join()
