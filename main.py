import argparse, datetime, imutils, json, time, cv2, threading
from imutils.video import VideoStream
from flask import Response, Flask, render_template
from mail import sending_email
#Szükséges modulok importálása.

def motion_detection(video_stream, from_address, to_address, password):
    # A függvény paraméterül kapja magát a video stream-ot valamint az
    # email elküldéséhez szükséges infromációkat.

    last_email_sending = 0
    # A script indításakor a segédváltozó amely az utolsó e-mail elküldésének
    # idejét jelzi nullára kerül beállításra.

    email_sending_interval = 60
    #Két e-mail küldés közötti idő alapértelmezetten 60 másodperce kerül beállításra.

    background = None
    # Háttér nullázása.
    while True:
        frame = video_stream.read()
        # A video stream-ból beolvasásra kerül az aktuális képkocka.

        timestamp = datetime.datetime.now()

        frame = imutils.resize(frame, width=500)
        #Újra méretezésre kerül a képkocka.

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Színesből szürkeárnyalatos kép előállítása.

        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        #Gaussian Blur szűrő alkalmazása.

        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

        if background is None:
            print("[INFO] Háttér számolása..")
            background = gray.copy().astype("float")
            continue
            # A háttér előállítása, konvertálása a képkockából, amennyiben ez korábban nem került elvégzésre.

        cv2.accumulateWeighted(gray, background, 0.5)
        #Egyébként pedig kiszámolásra kerül a bemeneti képkocka
        #és a már meglévő háttér közötti súlyozott átlagot.

        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(background))
        # Az abszolút különbség kiszámolásra került a bemeneti képkocka és a
        # háttér között


        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
        # Az összes pixel amelynek különbsége nagyobb a paraméternél kapott értéknél, az 255 (fehér) re kerül állításra
        # máskülönben 0-ra (fekete) kerülnek beállításra.

        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        # A zajok eltüntésére kerül felhasználásra a fenti két függvény.


        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # Kontúrok detektálása a thresh objektumból.

        for c in cnts:
        # A kontúrok végig iterálása.

            if cv2.contourArea(c) < conf["min_area"]:
                continue
            # Ha a kontúr túl kicsi, figyelmen kívül hagyja.

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # A háttér előállítása, konvertálása a képkockából, amennyiben ez korábban nem került elvégzésre.

            if ((time.time() - last_email_sending) > email_sending_interval):
            # Amennyiben a korábbi e-mail küldése óta már eltelt a beálított idő megtörténik az e-mail elküldése.

                last_email_sending = time.time()
                #Akitualizálásra kerül a segéd változó.

                timestamp = datetime.datetime.now()
                ts = timestamp.strftime("%d_%B_%Y %I_%M_%S%p")
                #időbélyegkerül elkésíztésre az egyedi fájl névhez.

                path = ts + ".jpg"
                # A kimentendő képkocka elérési útjának megadása.
                if (cv2.imwrite(path, frame)):
                    print("[INFO] A kep mentese sikeres, e-mail küldése folyamatban..")

                    sending_email(path, from_address, to_address, password)
                    #amennyiben sikeres a képkocka kimentése az e-mail üzenet elküldésre kerül.
                else:
                    print("A kep mentese sikertelen")

        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)
        #A képkockára rárajzolásra kerül az aktuális időbélyeg

        if conf["show_video"]:
            cv2.imshow("PI Security Camera", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
        # Amennyiben szükséges az aktuális képkocka megjelenítésre kerül.


def stream(video_stream):
    while True:
        frame = video_stream.read()
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        # A böngészők számára megfelelő formátumúra kerül kódolásra a képkocka, és azt visszaadajuk a függvényből.


def app_run(ip,port):
    app.run(host=ip, port=port, debug=True, threaded=True, use_reloader=False)
    #A Flask applikáció elindítására szolgáló függvény, melynke paraméterei határozzak meg az elérési IP címet és port számot.


app = Flask(__name__)
#A Flask objektum inicializálása.

@app.route("/")
def index():
    return render_template("index.html")
# A rendre_template meghívásra került a készített HTML fájlra.
# AZ app.route jelzi hogy az alattá található fügvény egy URL végpont amely a megadott heylen érhető el.

@app.route("/video_feed")
def video_feed():
    return Response(stream(video_stream), mimetype="multipart/x-mixed-replace; boundary=frame")
#Fenti függvény a videó stream outputja, mely byte töbé került kódolásra, mely formátumot a böngésző használni tudja a megjelenítéshez.


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True, help="A konfigurációs fájl elérési útvonala.")
    args = vars(ap.parse_args())
    #A parancssoros argumentumok feldolgozása.

    conf = json.load(open(args["conf"]))
    #A szükséges beállításokat tartalmazó json fájl beolvasása.

    from_address = conf["fromaddr"]
    to_address = conf["toaddr"]
    password = conf["password"]
    ip = conf["ip"]
    port = conf["port"]
    #A felhasználó által megadott paraméterek felhasználása.

    # video_stream = VideoStream(usePiCamera=1).start()
    video_stream = VideoStream(src=0).start()
    #A kamera elindítása elindítása.

    thread1 = threading.Thread(target=app_run, args=(ip,port,))
    thread1.start()
    thread2 = threading.Thread(target=motion_detection, args=(video_stream, from_address, to_address, password))
    thread2.start()
    #A párhuzamos futás elérése érdekében threadok felhasználásával kerül elindításra a mozgásrézékelést végrehajtó
    #illetve a video streamot végrehajtó függvények.


