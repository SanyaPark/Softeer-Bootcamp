from multiprocessing import Process, Queue
import time
# 재웅님 코드: args가 list type

def push_to_queue(queue:Queue, items):
    print("pushing items to queue")
    
    for index, item in enumerate(items, start=1):
        queue.put((index, item))
        print(f"item no: {index} {item}")
        time.sleep(0.3)
    
def pop_from_queue(queue:Queue):
    print("popping items from queue:")
    # item_number = 0
    while not queue.empty():
        item_number, item = queue.get()
        print(f"item no: {item_number-1} {item}")
        time.sleep(0.3)



if __name__ == "__main__":
    colors = ["Red", "Green", "Blue", "Black"]
    
    queue = Queue()
    
    producer = Process(target=push_to_queue, args=(queue, colors))
    consumer = Process(target=pop_from_queue, args=(queue,))
    
    producer.start()
    producer.join()
    
    consumer.start()
    consumer.join()