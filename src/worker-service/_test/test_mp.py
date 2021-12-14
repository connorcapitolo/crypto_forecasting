import multiprocessing
import time
import os


def sleepy_man():
    print('Starting to sleep')
    time.sleep(1)
    print('Done sleeping')


print("No multiprocessing...")
tic = time.time()
sleepy_man()
sleepy_man()
toc = time.time()

print('Done in {:.4f} seconds'.format(toc-tic))

print("===========================")
print("Multiprocessing...")
tic = time.time()
p1 = multiprocessing.Process(target=sleepy_man)
p2 = multiprocessing.Process(target=sleepy_man)
p1.start()
p2.start()
toc = time.time()

print('Done in {:.4f} seconds'.format(toc-tic))


print("===========================")
print("Multiprocessing...")
tic = time.time()
p1 = multiprocessing.Process(target=sleepy_man)
p2 = multiprocessing.Process(target=sleepy_man)
p1.start()
p2.start()
p1.join()
p2.join()
toc = time.time()

print('Done in {:.4f} seconds'.format(toc-tic))


print("===========================")
print("Multiprocessing... with Queue")


NUM_PROCESSES = multiprocessing.cpu_count() - 1

the_queue = multiprocessing.Queue()


def worker_main(queue):
    print(os.getpid(), "working")
    while True:
        item = queue.get(True)
        print(os.getpid(), "got", item)
        time.sleep(1)  # simulate a "long" operation


the_pool = multiprocessing.Pool(3, worker_main, (the_queue,))

for i in range(5):
    the_queue.put("hello")
    the_queue.put("world")


time.sleep(10)
