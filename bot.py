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

def checkuser(telegramid):
    sql.execute(f"SELECT tele_id FROM user WHERE tele_id ='{telegramid}'")
    user = sql.fetchall()
    if len(user) == 1:
        return True
    else:
        return False

def checkbarang(idbarang):
    barang_id = int(idbarang)
    sql.execute(f"SELECT id_barang FROM barang WHERE id_barang ='{barang_id}'")
    barang = sql.fetchall()
    if len(barang) == 1:
           return True
    return False

def idorder(idbarang,idorang):
    now = datetime.datetime.now()
    seq = now.strftime("%Y%m%d%H%M")
    stridorang = str(idorang)
    stridbarang = str(idbarang)
    idorder = int(seq+stridorang+stridbarang)
    return idorder
    

def isadmin(idtelegram):
    sql.execute(f"SELECT tele_id FROM admin WHERE tele_id ='{idtelegram}'")
    admin = sql.fetchall()
    if len(admin) == 1:
        return True
    else:
        return False

def log(message,perintah):
    tanggal = datetime.datetime.now()
    tanggal = tanggal.strftime('%d-%B-%Y')
    nama_awal = message.chat.first_name
    nama_akhir = message.chat.last_name
    id_user = message.chat.id
    text_log = f'{tanggal}, {id_user}, {nama_awal}, {nama_akhir}, {perintah}\n'
    log_bot = open('logbot.txt', 'a')
    log_bot.write(text_log)
    log_bot.close()

# welcome message handler
@bot.message_handler(commands=["start"])
def send_welcome(message):
    log(message, message.text)
    bot.reply_to(message, "  Halo Selamat Datang. Silahkan ketik /help untuk menemukan perintah")

# @bot.message_handler(
#     func=lambda message: message.text is not None and "zayank" in message.text
# )
# def message_list(message):
#     chat_id = message.from_user.id
#     text = message.text.split(" ")
#     perintah = text[1]
#     if perintah == "order":
#         order(message)
#     if perintah == "list":
#         product_list(message)
#     if perintah == "daftar":
#         daftar(message)
#     else:
#         bot.send_message(chat_id, "RA NGERTI BROW")

#Handler Perintah order
@bot.message_handler(commands=["order"])
def order(message):
    log(message, message.text)
    no_id = int(message.chat.id)
    if checkuser(no_id):
        bot.send_message(no_id, "ANDA TERDAFTAR, OK LANJUT")
        #try expect to fix value and index error
        try:
            text = message.text.split(" ")
            barang = int(text[1])
            jmlh = int(text[2])
            if checkbarang(barang):
                pass
            else:
                bot.send_message(no_id,"Barang tidak tersedia")
            sql.execute(f"SELECT harga FROM barang WHERE id_barang ='{barang}'")
            hargabarang = sql.fetchall()
            harga = int(hargabarang[0][0])
            kode = idorder(no_id, barang)
            waktu = datetime.datetime.now()
            total = jmlh*harga
            insert = f"INSERT INTO list_order(id_order,tele_id,barang,jmlh, total, created_at) VALUES ('{kode}','{no_id}','{barang}','{jmlh}','{total}','{waktu}')"
            sql.execute(insert)
            db.commit()
            bot.send_message(no_id, "Ok Barang Berhasil Dipesan")
        except IndexError:
            bot.send_message(no_id, "Format tidak sesuai")
        except ValueError:
            bot.send_message(no_id, "Isi Sesuai ID Barang")
    else:
        bot.send_message(
            no_id, "DAFTAR DULU BOUSS. KETIK /help, untuk melakukan pendaftaran"
        )


#Handler Perintah list
@bot.message_handler(commands=["list"])
def product_list(message):
    log(message, message.text)
    chat_id = message.chat.id
    sql.execute("SELECT id_barang, nama, harga FROM barang")
    barang = sql.fetchall()
    for x in barang:
        id_barang = x[0]
        nama = x[1]
        harga = x[2]
        pesan = f"ID BARANG : {id_barang}\nNAMA BARANG : {nama}\nHARGA BARANG : Rp.{harga}\n"
        bot.send_message(chat_id, pesan)

#Handler Perintah daftar
@bot.message_handler(commands=["daftar"])
def daftar(message):
    log(message, message.text)
    chat_id = message.chat.id
    bot.send_message(chat_id,"format daftar :\n\n"
                            "/daftar[spasi]nama[spasi]alamat")
    if checkuser(chat_id):
        bot.send_message(chat_id, "Data has found")
    else:
        try:
            text = str(message.text)
            identitas = text.split(" ")
            nama = identitas[1]
            alamatarray = identitas[2::]
            alamat = ' '.join(map(str, alamatarray))
            insert = f"INSERT INTO user (tele_id,nama,alamat) VALUES ({chat_id},'{nama}','{alamat}')"
            sql.execute(insert)
            db.commit()
            bot.send_message(chat_id,"OK ANDA SUDAH TERDAFTAR")
        except IndexError:
            bot.send_message(chat_id, "SALAH FORMAT")

#handler help
@bot.message_handler(commands=["help"])
def help(message):
    log(message, message.text)
    first_name = str(message.from_user.first_name)
    last_name = str(message.from_user.last_name)
    bot.reply_to(message, f"Selamat Datang Ke Bot Pelayanan Kami {first_name} {last_name}\n\n"
                            "Untuk melakukan pendaftaran silakan ketik sesuai format /daftar[spasi]nama[spasi]alamat\n\n"
                            "Untuk mengecek list kode barang barang silakan ketik /list\n\n"
                            "untuk melakukan pengorderan silahkan ketik sesuai format /order barang banyak barang\n\n"
                            "Untuk mengecek orderlist yang telah dipesan ketik /orderlist")


#handler  orderlist
@bot.message_handler(commands=["orderlist"])
def orderlist(message):
    log(message, message.text)
    tele_id = int(message.chat.id)
    try:
        sql.execute("SELECT list_order.id_order,user.nama,barang.nama,list_order.total,list_order.jmlh,list_order.created_at FROM list_order INNER JOIN user ON list_order.tele_id = user.tele_id INNER JOIN barang ON list_order.barang = barang.id_barang WHERE list_order.tele_id = %s" % (tele_id))
        data = sql.fetchall()
        for datauser in data:
            id_order = datauser[0]
            nama_user = datauser[1]
            nama_barang = datauser[2]
            total = datauser[3]
            jmlah = datauser[4]
            tanggal = datauser[5]
            pesan = "ID ORDER = %s\nNama User = %s\nNama Barang = %s\nTotal Pembelian = %s\nJumlah Pembelian = %s\nTanggal Pemesanan = %s\n" % (id_order,nama_user,nama_barang,total,jmlah,tanggal)
            bot.send_message(tele_id,pesan)
    except IndexError :
        bot.send_message(tele_id,"Anda Belum Melakukan Pesanan")
    except Exception :
        bot.send_message(tele_id,"Saya tidak memahami apa yang anda katakan")


@bot.message_handler(commands=["laporan"])
def laporan(message):
    log(message, message.text)
    tele_id = int(message.chat.id)
    if isadmin(tele_id):
        sql.execute("SELECT list_order.id_order, user.nama, barang.nama, user.alamat, list_order.total, list_order.jmlh, list_order.created_at FROM list_order INNER JOIN user ON list_order.tele_id = user.tele_id INNER JOIN barang ON list_order.barang = barang.id_barang")
        data = sql.fetchall()
        if len(data) >= 1:
            for datauser in data:
                id_order = datauser[0]
                nama_user = datauser[1]
                nama_barang = datauser[2]
                alamat = datauser[3]
                total = datauser[4]
                jmlah = datauser[5]
                tanggal = datauser[6]
                pesan = f"ID ORDER = {id_order}\nNama User = {nama_user}\nAlamat = {alamat}\nNama Barang = {nama_barang}\nTotal Pembelian = {total}\nJumlah Pembelian = {jmlah}\nTanggal Pemesanan = {tanggal}\n"
                bot.send_message(tele_id,pesan)
        else:
            bot.send_message(tele_id,"Blom Ada Pembelian")
    else:
        bot.reply_to(message,"LU SAPA ANJER")



print("bot is berlari")
bot.polling()
