# Replay a log file to load a test server

import logging, re, sys, time, threading, traceback, httplib, pdb

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

log_parse = re.compile(
    r"\d+[.]\d+[.]\d+[.]\d+" # ip
    r"\s+"
    r"\S+" # remote login
    r"\s+"
    r"\S+" # auth user
    r"\s+"
    r"\["
    r"(\d\d)/([A-Z][a-z][a-z])/(\d\d\d\d):(\d\d):(\d\d):(\d\d)"
    r"(?: [^ \t\]]+)?"
    r"\]" # date
    r"\s+"
    r'"([^"]+)"' # request
    r"\s"
    ).match

months = dict(
    Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6,
    Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12,
    )

queue = []

def read(args=None):
    if args is None:
        args = sys.argv[1:]

    good = bad = get = 0
    for fname in args:
        for line in open(fname):
            m = log_parse(line)
            if m is None:
                bad += 1
                continue

            try:
                day, month, year, hour, minute, second, request = m.groups()

                month = months[month]
                t = time.mktime(
                    (int(year), month, int(day),
                     int(hour), int(minute), int(second),
                     0, 0, 0))

                url = request.split()
                url.pop()
                method = url.pop(0)
                url = '%20'.join(url)
                if method == 'GET':
                    get += 1
                queue.append((t, url))

                good += 1
            except:
                print 'trouble parsing', line
                traceback.print_exc()
                bad += 1
                
                
    print good, bad, get

def process_queue(server):
    results = {}
    while 1:
        try:
            t, url = queue.pop()
        except IndexError:
            break

##         t -= time.time()
##         if t > 0:
##             time.sleep(t)

        conn = httplib.HTTPConnection(server)
        conn.request("GET", url)
        r = conn.getresponse()
        results[r.status] = results.get(r.status, 0) + 1
        r.read()
        conn.close()
##         sys.stdout.write('.')
##         sys.stdout.flush()

    print results
            

        

def main():
    global queue
    queue = []

    args = sys.argv[1:]
    server = args.pop(0)

    read(args)
    queue.reverse()
    threads = []
##    process_queue()
    for i in range(50):
        thread = threading.Thread(target=process_queue, args=(server,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
            
if __name__ == '__main__':
    main()
