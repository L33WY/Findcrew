import bcrypt

password = u"Dawid321"

hasedPassword = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

print(hasedPassword)