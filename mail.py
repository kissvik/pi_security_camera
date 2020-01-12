
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

#Az e-mail megküldéséhez az smtplib modul, az e-mail létrehozásához pedig az e-mail modul került felhasználásra.

def sending_email(path, honnan, hova, jelszo):

	msg = MIMEMultipart()
	#Példányosításra kerül a MIMEMultipart osztály.

	msg['From'] = honnan
	msg['To'] = hova
	msg['Subject'] = "Biztonsági kamera frissítés!"
	#Az osztály feladó, küldő és tárgy részei megadásra kerülnek.

	body = "Üdv! Mozgást érzékeltem, mellékelem a készült fényképet!"
	#String-ként megadásra került az üzenet törzse.
	
	msg.attach(MIMEText(body, 'plain'))
	#Levél törzsének hozzáadása.

	filename = path
	attachment = open( path,"rb")
	#A mellékelt file megnítása. Első paraméter a fájl elérési útját adja meg, és mivel
	#kép fájl kerül elküldésre így ezt "rb" módban hajtjuk végre.

	p = MIMEBase('application', 'octet-stream') 
	#Példányosításra került a MIMEBase osztály.

	p.set_payload((attachment).read())
	encoders.encode_base64(p)
	# A melléklet hozzáadása, és az üzenet kódolása.
	
	p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
	#Fejléc hozzácsatolása.

	msg.attach(p)
	#A két osztály egyesítése.

	s = smtplib.SMTP('smtp.gmail.com', 587)
	#A sikeres küldéshez létrehozásra kerül egy session, amivel felépítjük az SMTP kapcsolatot.
	#Paraméterként megadásra kerül a szerver címe és a használt port.

	s.starttls()
	#Biztonsági okokból az SMTP kapcsolat átálításra kerül TLS módba.
	#A TLS (Transport Layer Security) az összes SMTP-parancsot titkosítja

	s.login(honnan, jelszo)
	#Bejelentkezés a küldő fiókba.

	text = msg.as_string()

	s.sendmail(honnan, hova, text)
	#Az üzenet elküldése.

	s.quit()
	#Session bezárása.