
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

   
def sending_email(path, honnan, hova, jelszo):
	fromaddr = honnan
	toaddr = hova
	
	msg = MIMEMultipart() 
		
	msg['From'] = fromaddr 
	msg['To'] = toaddr 
	msg['Subject'] = "Biztonsági kamera frissítés!"
	
	body = "Üdv! Mozgást érzékeltem, mellékelem a készült fényképet!"
	
	msg.attach(MIMEText(body, 'plain'))   
	filename = path
	attachment = open( path,"rb") 
	p = MIMEBase('application', 'octet-stream') 
	p.set_payload((attachment).read()) 
	encoders.encode_base64(p) 
	
	p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
	msg.attach(p) 
	s = smtplib.SMTP('smtp.gmail.com', 587) 
	s.starttls() 
	
	s.login(fromaddr, jelszo) 
	text = msg.as_string() 
	s.sendmail(fromaddr, toaddr, text) 
	s.quit() 