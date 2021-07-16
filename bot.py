import telebot
import mysql.connector
import configparser
import  datetime

#configparser
config = configparser.ConfigParser()
config.read("setting.ini")

#config token
API_TOKEN = config["bot"]["token"]
bot = telebot.TeleBot(API_TOKEN)

#config database
user = config["db"]["user"]
password = ""
database = config["db"]["database"]

#Setting SQL
db = mysql.connector.connect(user=user, password=password, database=database)
sql = db.cursor()

def checkuser(telegramid): #mendefinisikan fungsi
    sql.execute(f"SELECT tele_id FROM user WHERE tele_id ='{telegramid}'") #mengeksekusi query untuk mengecek user
    user = sql.fetchall() # mengambil hasil dari eksekusi query
    if len(user) == 1: #if jika banyak data sama dengan 1
        return True # mengembalikan nilai true
    else: # else jika tidak ada data
        return False # mengembalikan nilai false

def checkbarang(idbarang): # mendefinisikan fungsi checkbarang
    barang_id = int(idbarang) # deklarasi variabel
    sql.execute(f"SELECT id_barang FROM barang WHERE id_barang ='{barang_id}'") # eksekusi query untuk mengecek barang
    barang = sql.fetchall() # mengambil data  dari hasil eksekusi query
    if len(barang) == 1: # if jika data sama dengan 1
           return True # mengembalikan nilai true
    return False # else jika data tidak sama dengan 1

def idorder(idbarang,idorang): # mendefinisikan fungsi idorder
    now = datetime.datetime.now() #mengambil fungsi datetime
    seq = now.strftime("%Y%m%d%H%M") # deklarasi variabel mengatur data yang diambil menjadi Year-Month-Day-Hours-Minutes
    stridorang = str(idorang) # deklarasi variabel 
    stridbarang = str(idbarang) #deklarasi variabel
    idorder = int(seq+stridorang+stridbarang) #menggabung variabel 
    return idorder # mengembalikan nilai variabel
    

def isadmin(idtelegram): # mendefinisikan fungsi isadmin
    sql.execute(f"SELECT tele_id FROM admin WHERE tele_id ='{idtelegram}'") # melakukan query select dengan parameter WHERE id telegram
    admin = sql.fetchall() # mengambil hasil query
    if len(admin) == 1: # if jika data sama dengan satu
        return True # mengembalikan nilai trus
    else: # else jika data tidak ada
        return False # mengembalikan false

def log(message,perintah): # mendefinisikan fungsi log
    tanggal = datetime.datetime.now() # deklarasi variabel untuk current datetime
    tanggal = tanggal.strftime('%d-%B-%Y') # mendeklarasikan aturan date day-month-Year
    nama_awal = message.chat.first_name #deklarasi variabel nama awal
    nama_akhir = message.chat.last_name #deklarasi variabel nama awal
    id_user = message.chat.id # deklarasi id user
    text_log = f'{tanggal}, {id_user}, {nama_awal}, {nama_akhir}, {perintah}\n' # format tulisan
    log_bot = open('logbot.txt', 'a') # membuka file logbot.txt dengan kondisi memasukkan text
    log_bot.write(text_log) # menulis variabel text log ke dalam file
    log_bot.close() # menutup file logbot.txt

# welcome message handler
@bot.message_handler(commands=["start"])
def send_welcome(message): # definisi fungsi welcome
    log(message, message.text) # memanggil fungsi log dengan parameter message dan message.text
    bot.reply_to(message, "  Halo Selamat Datang. Silahkan ketik /help untuk menemukan perintah") # membalas text user

#Handler Perintah order
@bot.message_handler(commands=["order"])
def order(message): # definisi fungsi order
    log(message, message.text) # memanggil fungsi log
    no_id = int(message.chat.id) # mendeklarasikan variabel dengan isi message.chat.id
    if checkuser(no_id): # if jika fungsi checkuser true
        bot.send_message(no_id, "ANDA TERDAFTAR, OK LANJUT") # mengirim kalimat ke user sesuai no_id
        #try expect to fix value and index error
        try:
            text = message.text.split(" ") # memisah text dengan kondisi spasi
            barang = int(text[1]) # deklarasi variabel barang
            jmlh = int(text[2]) # deklarasi variabel jmlh
            if checkbarang(barang): # if jika checkbarang true
                sql.execute(f"SELECT harga FROM barang WHERE id_barang ='{barang}'") # eksekusi query select harga barang
                hargabarang = sql.fetchall() # mengambil hasil dari query
                harga = int(hargabarang[0][0]) # mendeklarasikan variabel
                kode = idorder(no_id, barang) # mendeklarasikan variabel
                waktu = datetime.datetime.now() # mendeklarasikan variabel
                total = jmlh*harga # mendeklarasikan variabel
                insert = f"INSERT INTO list_order(id_order,tele_id,barang,jmlh, total, created_at) VALUES ('{kode}','{no_id}','{barang}','{jmlh}','{total}','{waktu}')"
                sql.execute(insert) # mengeksekusi query insert
                db.commit() # melakukan commit
                bot.send_message(no_id, "Ok Barang Berhasil Dipesan") # mengirim pesan ke user
            else: # else ketika checkbarang false
                bot.send_message(no_id,"Barang tidak tersedia") # mengirim pesan ke user
        except IndexError: # menghandel error index 
                bot.send_message(no_id, "Format tidak sesuai") # mengirim pesan ke user
        except ValueError: # menghandel error nilai
                bot.send_message(no_id, "Isi Sesuai ID Barang") # mengirim pesan ke user
    else: # else ketika checkuser false
        bot.send_message(
            no_id, "DAFTAR DULU BOUSS. KETIK /help, untuk melakukan pendaftaran"
        ) # mengirim pesan ke user


#Handler Perintah list
@bot.message_handler(commands=["list"])
def product_list(message): # mendefinisikan product
    log(message, message.text) # memanggil fungsi log
    chat_id = message.chat.id # mendeklarasikan variabel chat_id
    sql.execute("SELECT id_barang, nama, harga FROM barang") # mengeksekusi query select ke tabel barang
    barang = sql.fetchall() # mengambil semua nilai hasil eksekusi query
    for x in barang: # melakukan loop pada setiap data di barang
        id_barang = x[0] # mendeklarasikan variabel id_barang
        nama = x[1] # mendeklarasikan variabel nama
        harga = x[2] # mendeklarasikan variabel harga
        pesan = f"ID BARANG : {id_barang}\nNAMA BARANG : {nama}\nHARGA BARANG : Rp.{harga}\n" # melakukan format string sesuai variabel
        bot.send_message(chat_id, pesan) # mengirim pesan ke user

#Handler Perintah daftar
@bot.message_handler(commands=["daftar"])
def daftar(message): # mendeklarasikan fungsi daftar
    log(message, message.text) # memanggil fungsi log
    chat_id = message.chat.id # mendeklarasikan variabel
    bot.send_message(chat_id,"format daftar :\n\n"
                            "/daftar[spasi]nama[spasi]alamat") # mengirimkan text ke user
    if checkuser(chat_id): # if jika checkuser true
        bot.send_message(chat_id, "Data Telah Ditemukan, Silahkan melakukan order") # mengirim pesan ke user
    else: # else ketika checkuser false
        try: # digunakan untuk mengatasi eror yang tidak terduga
            text = str(message.text) # mendeklarasikan variabel text
            identitas = text.split(" ") # # mendeklarasikan variabel
            nama = identitas[1] # mendeklarasikan variabel text
            alamatarray = identitas[2::] # mendeklarasikan variabel text
            alamat = ' '.join(map(str, alamatarray)) # mendeklarasikan variabel text
            insert = f"INSERT INTO user (tele_id,nama,alamat) VALUES ({chat_id},'{nama}','{alamat}')" 
            sql.execute(insert) # mengeksekusi query sesuai variabel
            db.commit() # melakukan commit
            bot.send_message(chat_id,"OK ANDA SUDAH TERDAFTAR") # mengirimkan text ke user
        except IndexError: # menangkap erorr index 
            bot.send_message(chat_id, "SALAH FORMAT") # mengirim text ke user

#handler help
@bot.message_handler(commands=["help"])
def help(message): # mendefisinikan fungsi help
    log(message, message.text) # memanggil fungsi log
    first_name = str(message.from_user.first_name) # mendeklarasikan variabel
    last_name = str(message.from_user.last_name) # mendeklarasikan variabel
    bot.reply_to(message, f"Selamat Datang Ke Bot Pelayanan Kami {first_name} {last_name}\n\n"
                            "Untuk melakukan pendaftaran silakan ketik sesuai format /daftar[spasi]nama[spasi]alamat\n\n"
                            "Untuk mengecek list kode barang barang silakan ketik /list\n\n"
                            "untuk melakukan pengorderan silahkan ketik sesuai format /order barang banyak barang\n\n"
                            "Untuk mengecek orderlist yang telah dipesan ketik /orderlist") # mengirim text help ke user


#handler  orderlist
@bot.message_handler(commands=["orderlist"])
def orderlist(message): # mendefinisikan fungsi orderlist
    log(message, message.text) # memanggil fungsi log
    tele_id = int(message.chat.id) # mendeklarasikan variabel
    try: # digunakan untuk mengatasi eror yang tidak terduga
        sql.execute(f"SELECT list_order.id_order,user.nama,barang.nama,list_order.total,list_order.jmlh,list_order.created_at FROM list_order INNER JOIN user ON list_order.tele_id = user.tele_id INNER JOIN barang ON list_order.barang = barang.id_barang WHERE list_order.tele_id = {tele_id}")
        data = sql.fetchall() #mengambil data dari query
        if len(data) > 0: # mengecek jika ada data
            for datauser in data: # melakukan loop pada setiap datauser di data
                id_order = datauser[0] # mendeklarasikan variabel
                nama_user = datauser[1] # mendeklarasikan variabel
                nama_barang = datauser[2] # mendeklarasikan variabel
                total = datauser[3] # mendeklarasikan variabel
                jmlah = datauser[4] # mendeklarasikan variabel
                tanggal = datauser[5] # mendeklarasikan variabel
                pesan = "ID ORDER = %s\nNama User = %s\nNama Barang = %s\nTotal Pembelian = %s\nJumlah Pembelian = %s\nTanggal Pemesanan = %s\n" % (id_order,nama_user,nama_barang,total,jmlah,tanggal)
                bot.send_message(tele_id,pesan) # mengirim text ke user
        else: # jika data tidak ada maka akan mengirim pesan
            bot.send_message(tele_id,"Anda Belum Melakukan Pesanan")
    except Exception : # menangkap eroor yang tidak diketahui
        bot.send_message(tele_id,"Saya tidak memahami apa yang anda katakan") # mengirim pesan ke user

# handler laporan
@bot.message_handler(commands=["laporan"])
def laporan(message): # mendeklarasikan fungsi laporan
    log(message, message.text) # memanggil fungsi log
    tele_id = int(message.chat.id) # mendeklarasikan variabel
    if isadmin(tele_id): # if jika isadmin adalah true
        sql.execute("SELECT list_order.id_order, user.nama, barang.nama, user.alamat, list_order.total, list_order.jmlh, list_order.created_at FROM list_order INNER JOIN user ON list_order.tele_id = user.tele_id INNER JOIN barang ON list_order.barang = barang.id_barang")
        data = sql.fetchall() # mengambil data dari query yang dieksekusi
        if len(data) >= 1: # jika banyak data lebih dari satu
            for datauser in data: # melakukan loop untuk setiap datauser didalam data
                id_order = datauser[0] # mendeklarasikan variabel
                nama_user = datauser[1] # mendeklarasikan variabel
                nama_barang = datauser[2] # mendeklarasikan variabel
                alamat = datauser[3] # mendeklarasikan variabel
                total = datauser[4] # mendeklarasikan variabel
                jmlah = datauser[5] # mendeklarasikan variabel
                tanggal = datauser[6] # mendeklarasikan variabel
                pesan = f"ID ORDER = {id_order}\nNama User = {nama_user}\nAlamat = {alamat}\nNama Barang = {nama_barang}\nTotal Pembelian = {total}\nJumlah Pembelian = {jmlah}\nTanggal Pemesanan = {tanggal}\n"
                bot.send_message(tele_id,pesan) # mengirim pesan ke user
        else: # jika banyak data tidak ada
            bot.send_message(tele_id,"Blom Ada Pembelian") # mengirim pesan ke user
    else: # else ketika isadmin false
        bot.reply_to(message,"Not Authorize") # mengirim pesan ke user


 
print("bot is berlari") # menampilkan bot is berlari di terminal
bot.polling() # mengambil data dari telegram
