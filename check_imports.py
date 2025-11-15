import sys
sys.path.insert(0, r'c:\Users\FARDIN\Desktop\telegram-academy-bot')
try:
    import bot
    import database
    import admin_handlers
    import excel_tools
    import student_handlers
    print('IMPORTS_OK')
    print('DB_PATH=', database.DB_PATH)
    database.init_db()
    print('DB_INIT_OK')
    txt = 'علیرضا - دوشنبه - 16:00 تا 17:30\nسارا - سه شنبه - 14:00 تا 15:30'
    bio = excel_tools.text_to_excel_bytes(txt)
    print('EXCEL_BYTES_LEN=', len(bio.getvalue()))
except Exception as e:
    import traceback
    traceback.print_exc()
