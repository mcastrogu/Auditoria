from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, usuario):
        self.id = id
        self.usuario = usuario

    def get_id(self):
        return str(self.id)
