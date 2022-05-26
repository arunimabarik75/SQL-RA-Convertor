from tkinter import *
from matplotlib.pyplot import text
from numpy import full
import cx_Oracle

screen = Tk(screenName="Main Screen")
screen.title("DBMS Innovative Assignment")
p1 = PhotoImage(file='icon.png')
screen.iconphoto(False, p1)
screen.geometry("1536x864")
canvas = Canvas()

canvas.create_line(0, 180, 1536, 180)
canvas.create_line(0, 182, 1536, 182)
canvas.create_line(600, 0, 600, 800)
canvas.create_line(602, 0, 602, 800)
canvas.pack(expand=1, fill=BOTH)

sentence = Entry(screen, width=30, font=(
    "Times New Roman", 20), borderwidth=10, relief=FLAT)
ddlQuery = Entry(screen, width=30, font=(
    "Times New Roman", 20), borderwidth=10, relief=FLAT)

ddllbl = Label(screen, text='', font=("Times New Roman", 12))
r1 = Label(text='20BCE016 Arunima Barik', font=("Times New Roman", 20))
r1.place(x=20, y=75)
r2 = Label(text='20BCE079 Gaurav Golchha', font=("Times New Roman", 20))
r2.place(x=20, y=120)
r3 = Label(text='20BCE012 Meet Amin', font=("Times New Roman", 20))
r3.place(x=20, y=30)
r4 = Label(text='Queries', font=("Times New Roman", 20))
r4.place(x=200, y=220)


def prj():
    strr = sentence.get()
    sentence.insert(len(strr), "π")


def sig():
    strr = sentence.get()
    sentence.insert(len(strr), "σ")


def orbut():
    strr = sentence.get()
    sentence.insert(len(strr), "∨")


def andbut():
    strr = sentence.get()
    sentence.insert(len(strr), "^")


def joinbut():
    strr = sentence.get()
    sentence.insert(len(strr), "X")


def intersectbut():
    strr = sentence.get()
    sentence.insert(len(strr), "∩")


def execute_SQL(sql_command):
    sql_command = sql_command[:-1]
    try:
        con = cx_Oracle.connect('practice/password@localhost:1521/xe')
        cursor = con.cursor()

        cursor.execute(sql_command)
        rows = cursor.fetchall()
        output = ''
        for row in rows:
            for element in row:
                output += "{}".format(element)+'\t'
            output += '\n'
        executed_screen = Toplevel(screen)
        executed_screen.title('SQL OUTPUT')
        txtbox = Text(executed_screen, width=100)
        txtbox.insert(INSERT, output)
        txtbox.pack()
        con.commit()
    except cx_Oracle.DatabaseError as e:
        executed_screen = Toplevel(screen)
        txtbox = Label(executed_screen,
                       text="There is a problem with Oracle: {}".format(e))
        txtbox.pack()
    except:
        print("Something bad just happened")
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def sql_to_ra_func(str):

    def format(str):
        str = str.replace(" ", "")
        temp = [ch for ch in str]
        for i in range(len(temp)):
            if temp[i] == '(':
                temp[i] = " ( "
            elif temp[i] == ')':
                temp[i] = " ) "
            elif temp[i] == 'σ':
                temp[i] = "σ "
            elif temp[i] == 'π':
                temp[i] = "π "
            elif temp[i] == 'X':
                temp[i] = " X "
        final = "".join(temp)
        return final.strip()

    def parts(str):
        str = str[:-1]
        from_ind = str.find('from')
        where_ind = str.find('where')

        if where_ind != -1:
            return str[:from_ind], str[from_ind:where_ind], str[where_ind:]
        else:
            return str[:from_ind], str[from_ind:], ""

    def stringify(list):

        if len(list) == 1:
            return '\nRA Query :\n'+list[0]

        str = 'Steps :\n'

        for x in list[:-1]:
            str += x
            str += '\n'

        str += 'RA Query :\n'+list[-1]
        return str

    def solve(str):
        sql = []
        select_clause, from_clause, where_clause = parts(str)
        select_clause1 = select_clause.replace('select', 'π')
        sql.append(select_clause+' --> '+select_clause1)

        from_clause1 = from_clause.replace('from', '(')
        from_clause1 = from_clause1.replace(',', ' X ')
        sql.append(from_clause+' --> '+from_clause1+' )')

        where_clause1 = where_clause.replace('where', 'σ')
        where_clause1 = where_clause1.replace('and', '^')
        where_clause1 = where_clause1.replace('or', '∨')

        star = select_clause.find('*')
        if star != -1:
            if where_clause == '':
                return [from_clause1+' )']
            else:
                sql = []
                sql.append(where_clause+' --> '+where_clause1)
                sql.append(where_clause1+from_clause1+')')
        elif where_clause1 == "":
            sql.append(format(select_clause1+from_clause1+')'))
        else:
            sql.append(where_clause+' --> '+where_clause1)
            sql.append(
                format(select_clause1+'('+where_clause1+from_clause1+'))'))
        return sql

    union = str.find('union')

    if union != -1:
        sql1 = solve(str[:union])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[union+5:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('union --> U')
        sql += sql2
        sql.append(str1[:-1] + " U "+str2)
        return stringify(sql)

    intersect = str.find('intersect')

    if intersect != -1:
        sql1 = solve(str[:intersect])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[intersect+9:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('intersect --> ∩')
        sql += sql2
        sql.append(str1[:-1] + " ∩ "+str2)
        return stringify(sql)

    minus = str.find('minus')

    if minus != -1:
        sql1 = solve(str[:minus])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[minus+5:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('minus --> -')
        sql += sql2
        sql.append(str1[:-1] + " - "+format(str2))
        return stringify(sql)

    return stringify(solve(str))


def ra_to_sql_func(str):

    def format(str):

        while True:
            if str[0] == '(':
                str = str.lstrip('(')
                str = str.rstrip(')')
            else:
                break

        str = str.replace(" ", "")
        temp = [ch for ch in str]
        for i in range(len(temp)):
            if temp[i] == '(':
                temp[i] = " ( "
            elif temp[i] == ')':
                temp[i] = " ) "
            elif temp[i] == 'σ':
                temp[i] = "σ "
            elif temp[i] == 'π':
                temp[i] = "π "
        final = "".join(temp)
        return final.strip()

    def columns(str):
        list = str.split(' ')
        return list[1]

    def conditions(str):
        list = str.split(' ')

        if list[3] != 'σ':
            return ""

        temp = [ch for ch in list[4]]

        for i in range(len(temp)):
            if temp[i] == '^':
                temp[i] = " and "
            if temp[i] == '∨':
                temp[i] = " or "

        final = "".join(temp)
        return final

    def tables(str):
        list = str.split(' ')

        if len(list) == 1:
            return list[0]
        elif list[3] == 'σ':
            temp = [ch for ch in list[6]]
        else:
            temp = [ch for ch in list[3]]

        for i in range(len(temp)):
            if temp[i] == 'X':
                temp[i] = ","

        final = "".join(temp)
        return final

    def stringify(list):

        if len(list) == 1:
            return 'SQL Query :\n'+list[0]

        str = 'Steps :\n'

        for x in list[:-1]:
            str += x
            str += '\n'

        str += 'SQL Query :\n'+list[-1]
        return str

    def solve(str):

        str = format(str)
        table = tables(str)

        pi = str.find('π')
        sigma = str.find('σ')

        if pi == -1:
            if sigma == -1:
                return ["select * from "+table+";"]
            else:
                list = str.split(' ')

                temp = [ch for ch in list[1]]

                for i in range(len(temp)):
                    if temp[i] == '^':
                        temp[i] = " and "
                    if temp[i] == '∨':
                        temp[i] = " or "

                final = "".join(temp)

                sql = []
                sql.append('σ '+list[1]+' --> '+'where '+final)
                sql.append('select * from '+table+' where '+final+';')
                return sql

        col = columns(str)
        cond = conditions(str)

        if cond:
            sql = []
            list = str.split(' ')

            sql.append('π '+list[1]+' --> select '+col)
            sql.append('σ '+list[4]+' --> where '+cond)
            sql.append(list[6]+' --> from '+table)
            sql.append("select "+col+" from "+table+" where "+cond+";")

            return sql

        else:
            sql = []
            list = str.split(' ')

            sql.append('π '+list[1]+' --> select '+col)
            sql.append(list[3]+' --> from '+table)
            sql.append("select "+col+" from "+table+";")

            return sql

    union = str.find('U')

    if union != -1:
        sql1 = solve(str[:union])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[union+1:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('U --> union')
        sql += sql2
        sql.append(str1[:-1] + " union "+str2)

        sqlcmd = sql[-1]
        return stringify(sql), sqlcmd

    intersect = str.find('∩')

    if intersect != -1:
        sql1 = solve(str[:intersect])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[intersect+1:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('∩ --> intersect')
        sql += sql2
        sql.append(str1[:-1] + " intersect "+str2)

        sqlcmd = sql[-1]
        return stringify(sql), sqlcmd

    minus = str.find('-')

    if minus != -1:
        sql1 = solve(str[:minus])
        str1 = sql1[-1]
        sql1 = sql1[:-1]

        sql2 = solve(str[minus+1:])
        str2 = sql2[-1]
        sql2 = sql2[:-1]

        sql = sql1
        sql.append('- --> minus')
        sql += sql2
        sql.append(str1[:-1] + " minus "+str2)

        sqlcmd = sql[-1]
        return stringify(sql), sqlcmd

    sqlcmd = solve(str)[-1]

    return stringify(solve(str)), sqlcmd


global sql_label
global ra_label
sql_label = Label(font=("Times New Roman", 20))
ra_label = Label(font=("Times New Roman", 20))


def get_positions(str):
    line = 1
    index = 0
    pos_lis = []
    temp = [ch for ch in str]
    for i in range(len(temp)):
        if(temp[i] == '\n'):
            line += 1
            index = 0
            continue
        if temp[i] == '∨' or temp[i] == '^' or temp[i] == 'σ' or temp[i] == 'π' or temp[i] == 'X' or temp[i] == 'U' or temp[i] == '∩':
            pos_lis.append([line, index])
        index += 1
    return pos_lis


def get_sub_pos(str):
    line = 1
    index = 0
    pos_lis = []

    i = 0
    while i < len(str):

        if str[i] == '\n':
            line += 1
            index = 0
            i += 1
            continue

        if str[i] == 'σ' or str[i] == 'π':
            temp_lis = []
            temp_lis.append(line)
            temp_lis.append(index+2)

            for j in range(i+1, len(str)):
                index += 1
                if str[j] == '\n' or str[j] == '-' or str[j] == ')' or str[j] == '(' or str[j] == '∩' or str[j] == 'U' or str[j] == 'X':
                    temp_lis.append(line)
                    temp_lis.append(index)
                    i = j

                    if str[j] == '\n':
                        line += 1

                    break

            if len(temp_lis) > 1:
                pos_lis.append(temp_lis)
        index += 1
        i += 1

    return pos_lis


def curr_func(status, str):
    ddllbl.place_forget()
    sqlcmd = ''
    if(status == 1):
        popup = Toplevel(screen)
        if status == 1:
            popup.title('SQL to RA ')
        else:
            popup.title('RA to SQL ')
        popup.geometry("1200x800")
        # try:
        sqlcmd = str
        res = sql_to_ra_func(str)
        # execute_SQL(str)
        positions = get_positions(res)
        positions1 = get_sub_pos(res)
        ra_label = Text(popup, font=(
            "Times New Roman", 20), width=80)
        ra_label.insert(INSERT, res)
        for x in positions:
            ra_label.tag_add("pi",  '{}.{}'.format(
                x[0], x[1]), '{}.{}'.format(x[0], x[1]+1))
            ra_label.tag_config("pi",
                                foreground='blue', font=("Times New Roman", 35))
        for x in positions1:
            ra_label.tag_add('columns', '{}.{}'.format(
                x[0], x[1]-1), '{}.{}'.format(x[2], x[3]))
            ra_label.tag_config('columns', font=(
                "Times New Roman", 15), offset=-4)
        ra_label.configure(state='disabled')
        sentence.delete(0, END)
        ra_label.place(x=30, y=60, height=400)

    elif status == 2:
        popup = Toplevel(screen)
        popup.geometry("1200x800")
        res, sqlcmd = ra_to_sql_func(str)
        positions = get_positions(res)
        positions1 = get_sub_pos(res)
        ra_label = Text(popup, font=(
            "Times New Roman", 20), width=80)
        ra_label.insert(INSERT, res)
        for x in positions:
            ra_label.tag_add("pi",  '{}.{}'.format(
                x[0], x[1]), '{}.{}'.format(x[0], x[1]+1))
            ra_label.tag_config("pi",
                                foreground='blue', font=("Times New Roman", 35))
        for x in positions1:
            ra_label.tag_add('columns', '{}.{}'.format(
                x[0], x[1]-1), '{}.{}'.format(x[2], x[3]))
            ra_label.tag_config('columns', font=(
                "Times New Roman", 15), offset=-4)
        ra_label.configure(state='disabled')
        sentence.delete(0, END)
        ra_label.place(x=30, y=60, height=400)

    execute_SQL(sqlcmd)
    # except:
    #     error_lbl = Label(popup, text='Invalid Input',
    #                       font=("Times New Roman", 20))
    #     error_lbl.place(x=100, y=390)


def sql_to_ra_btn():
    global status
    status = 1
    sentence.place(x=860, y=270, height=40)
    prjbtn.place_forget()
    sigbtn.place_forget()
    ra_label.place_forget()
    sql_label.place_forget()
    orbtn.place_forget()
    andbtn.place_forget()
    joinbtn.place_forget()
    intersectbtn.place_forget()
    submitbtn.place(y=450, x=1000)


def ra_to_sql_btn():
    global status
    status = 2
    prjbtn.place(x=900, y=400)
    sigbtn.place(x=1200, y=400)
    orbtn.place(x=1050, y=400)
    andbtn.place(x=900, y=470)
    joinbtn.place(x=1050, y=470)
    intersectbtn.place(x=1200, y=470)
    sentence.place(x=860, y=270, height=40)
    ra_label.place_forget()
    sql_label.place_forget()
    submitbtn.place(y=650, x=1000)


def submit():
    sentence_text = sentence.get()
    curr_func(status, sentence_text)


def ddlFun():
    ddlq = ddlQuery.get()
    try:
        con = cx_Oracle.connect('practice/password@localhost:1521/xe')
        cursor = con.cursor()
        ddlq = ddlq[:-1]
        cursor.execute(ddlq)
        ddllbl.config(text="Successful", font=("Times New Roman", 20))
        ddllbl.place(x=250, y=600)
        con.commit()
    except cx_Oracle.DatabaseError as e:
        ddllbl.config(text="There is a problem with Oracle {}".format(e))
        ddllbl.place(x=50, y=600)
    except:
        ddllbl.config(text="Something bad happened")
        ddllbl.place(x=50, y=600)


sql_to_ra = Button(screen, text='SQL TO RA',
                   command=sql_to_ra_btn, font=("Times New Roman", 20))
ra_to_sql = Button(screen, text='RA TO SQL',
                   command=ra_to_sql_btn, font=("Times New Roman", 20))
submitbtn = Button(screen, text='Submit', command=submit,
                   font=("Times New Roman", 20))
prjbtn = Button(screen, text='π', command=prj, font=("Times New Roman", 20))
sigbtn = Button(screen, text='σ', command=sig, font=("Times New Roman", 20))
ddlbtn = Button(screen, text='Execute', command=ddlFun,
                font=("Times New Roman", 20))
orbtn = Button(screen, text='∨', command=orbut, font=("Times New Roman", 20))
andbtn = Button(screen, text='^', command=andbut, font=("Times New Roman", 20))
joinbtn = Button(screen, text="X", command=joinbut,
                 font=("Times New Roman", 20))
intersectbtn = Button(screen, text='∩', command=intersectbut,
                      font=("Times New Roman", 20))


sql_to_ra.place(x=800, y=70)
ra_to_sql.place(x=1200, y=70)
ddlQuery.place(x=60, y=270, height=40)
ddlbtn.place(x=220, y=450)


screen.mainloop()
