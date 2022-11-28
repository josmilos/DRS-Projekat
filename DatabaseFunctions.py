import sqlite3

#TREBA DA SE POZIVA PRI POKRETANJU APLIKACIJE
def InitializeDatabase():
    conn = sqlite3.connect('drs_projekat.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_schema WHERE type='table'")
    lista_tabela = c.fetchall()
    if lista_tabela.__len__() != 0:
        return
    
    c.execute("""CREATE TABLE korisnici (
        ime TEXT,
        prezime TEXT,
        adresa TEXT,
        grad TEXT,
        drzava TEXT,
        broj telefona TEXT,
        email TEXT PRIMARY KEY,
        lozinka TEXT,
        stanje INTEGER,
        verifikovan TEXT
    )""")
    conn.commit()
    conn.close()

#TREBA DA SE POZIVA KOD REGISTRACIJE
#VRACA FALSE AKO JE EMAIL VEC KORISCEN, VRACA TRUE AKO JE USPESNO DODAO KORISNIKA
def AddNewKorisnik(ime, prezime, adresa, grad, drzava, broj_telefona, email, lozinka):
    conn = sqlite3.connect('drs_projekat.db')
    c = conn.cursor()
    c.execute("SELECT email from korisnik WHERE email=?", (email, ))
    rez = c.fetchone()
    if rez != None:
        return False
    c.execute("INSERT INTO korisnici VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ime, prezime, adresa, grad, drzava, broj_telefona, email, lozinka, 0, "NE"))
    conn.commit()
    conn.close()
    return True

def DeleteKorisnik(email, lozinka):
    conn = sqlite3.connect('drs_projekat.db')
    c = conn.cursor()
    c.execute("DELETE FROM korisnici WHERE email = ? AND lozinka = ?", (email, lozinka))
    conn.commit()
    conn.close()

def GetKorisnik(email, lozinka):
    conn = sqlite3.connect('drs_projekat.db')
    c = conn.cursor()
    c.execute("SELECT * FROM korisnici WHERE email = ? AND lozinka = ?", (email, lozinka))
    rez = c.fetchone()
    conn.close()
    return rez