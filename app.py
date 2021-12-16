import bcrypt
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user

app = Flask(__name__)
login_manager = LoginManager();
login_manager.init_app(app);
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jckeilifwqadam:def9be2570de873b44f0e4541501aff4b926f8f3e992509254569ad6341e0ca1@ec2-184-73-25-2.compute-1.amazonaws.com:5432/dc6lpemuj67vep'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='aloha'

db = SQLAlchemy(app)
bcryp = Bcrypt(app)


class Usuarios(UserMixin,db.Model):
    __tablename__= "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email=email
        self.password=password

class Editorial(db.Model):
    __tablaname__ = "editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial=nombre_editorial

class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)

    #Relacion
    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, id_editorial, id_autor, id_genero):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.id_editorial = id_editorial
        self.id_autor = id_autor
        self.id_genero = id_genero

class Autor(db.Model):
    __tablaname__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(80))
    fecha_nac = db.Column(db.Date)
    nacionalidad = db.Column(db.String(40))

    def __init__(self, nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionalidad = nacionalidad

class Genero(db.Model):
    __tablaname__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(80))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero


class MisFavoritos(db.Model):
    __tablaname__ = "misfavoritos"
    id_lista_favoritos = db.Column(db.Integer, primary_key=True)
    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    def __init__(self, id_libro, id_usuario):
        self.id_libro = id_libro
        self.id_usuario = id_usuario


@app.route("/")
def index():
    return render_template("signIn/index.html")

@app.route("/login", methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    consulta_usuario = Usuarios.query.filter_by(email=email).first()
    if bcryp.check_password_hash(consulta_usuario.password, password):
        login_user(consulta_usuario)
        return redirect("favoritos")
    else:
        return redirect("/")

#inician favoritos
@app.route("/favoritos")
@login_required
def inicio():
    print(str(current_user.id))
    return render_template("favoritos/index.html")

@login_manager.user_loader
def user_loader(user_id):
    return Usuarios.query.get(user_id)

@app.route("/cargarFavoritos", methods=['POST'])
@login_required
def cargarFavoritos():
    librosConsulta = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).join(MisFavoritos,Libro.id_libro==MisFavoritos.id_libro).add_columns(MisFavoritos.id_lista_favoritos,MisFavoritos.id_usuario,Libro.id_libro, Genero.nombre_genero, Libro.titulo_libro, Libro.volumen, Libro.fecha_publicacion, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial)
    return render_template("favoritos/tabla_favoritos.html",libros=librosConsulta,usuario=current_user.id)

@app.route("/eliminarFavorito", methods=["POST"])
def eliminarFavorito():
    idFavorito = request.form["idFavorito"]
    favorito = MisFavoritos.query.filter_by(id_lista_favoritos=int(idFavorito)).delete()
    #asignacion
    db.session.commit()
    return ("Favorito eliminado con éxito")
#terminan favoritos

#inician libros
@app.route("/libros")
def libros():
    return render_template("libros/index.html")

@app.route("/cargarLibros",methods=['POST'])
def cargarLibros():
    librosConsulta = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.id_libro, Genero.nombre_genero, Libro.titulo_libro, Libro.volumen, Libro.fecha_publicacion, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial)
    return render_template("libros/tabla_libros.html", libros = librosConsulta)

@app.route("/registralibro")
def registrar_libro():
    autorConsulta = Autor.query.all()
    generoConsulta = Genero.query.all()
    editorialConsulta = Editorial.query.all()
    return render_template("registrolibro.html", autores = autorConsulta, generos = generoConsulta, editoriales = editorialConsulta)

@app.route("/agregarFavorito",methods=['POST'])
@login_required
def agregarFavorito():
    idLibro = request.form["idLibro"]
    usuario  = current_user.id
    favorito = MisFavoritos(id_libro=idLibro, id_usuario=usuario)
    db.session.add(favorito)
    db.session.commit()
    return("Favorito agregado con éxito")

@app.route("/registrarLibro", methods=["POST"])
def registrarLibro():
    nombreLibro = request.form["nombreLibro"]
    fechaPublic = request.form["fecha"]
    paginas = request.form["numeroLibro"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    genero = request.form["genero"]
    autor = request.form["autor"]
    libro = Libro(titulo_libro=nombreLibro, fecha_publicacion=fechaPublic, numero_paginas=paginas, formato=formato, volumen=volumen, id_editorial=editorial, id_genero=genero, id_autor=autor)
    db.session.add(libro)
    db.session.commit()
    return "Libro registrado"

@app.route("/cargarAutoresNuevoLibro",methods=['POST'])
def cargarAutoresNuevoLibro():
    autorConsulta = Autor.query.all()
    return render_template("libros/select_autor.html", autores = autorConsulta)

@app.route("/cargarGenerosNuevoLibro",methods=['POST'])
def cargarGenerosNuevoLibro():
    generoConsulta = Genero.query.all()
    return render_template("libros/select_genero.html", generos = generoConsulta)

@app.route("/cargarEditorialesNuevoLibro",methods=['POST'])
def cargarEditorialesNuevoLibro():
    editorialesConsulta = Editorial.query.all()
    return render_template("libros/select_editorial.html", editoriales = editorialesConsulta)

@app.route("/cargarDetalleLibro",methods=['POST'])
def cargarDetalleLibro():
    ID = request.form["idLibro"]
    libros = Libro.query.filter_by(id_libro = int(ID)).first()
    genero = Genero.query.all()
    autor = Autor.query.all()
    editorial = Editorial.query.all()
    return render_template("libros/detalle_libro.html", libro = libros, generos = genero, autores = autor, editoriales = editorial)

@app.route("/modificarLibro", methods=["POST"])
def modificarLibro():
    idlibro = request.form["idlibro"]
    nombreLibro = request.form["nombreLibro"]
    fechaPublic = request.form["fecha"]
    paginas = request.form["numeroLibro"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    genero = request.form["genero"]
    autor = request.form["autor"]
    libro = Libro.query.filter_by(id_libro=int(idlibro)).first()
    libro.titulo_libro = nombreLibro
    libro.fecha_publicacion = fechaPublic
    libro.numero_paginas = paginas
    libro.formato = formato
    libro.volumen = volumen
    libro.id_editorial= editorial
    libro.id_genero = genero
    libro.id_autor = autor
    db.session.commit()
    return ("Libro modificado con éxito")

@app.route("/eliminarLibro", methods=["POST"])
def eliminarLibro():
    idLibro = request.form["idLibro"]
    libro = Libro.query.filter_by(id_libro=int(idLibro)).first()
    #asignacion
    db.session.delete(libro)
    db.session.commit()
    return ("Libro eliminado con éxito")
#terminan libros

#Inician autores
@app.route("/autores")
def autores():
    return render_template("autores/index.html")

@app.route("/cargarAutores",methods=['POST'])
def cargarAutores():
    autorConsulta = Autor.query.all()
    return render_template("autores/tabla_autores.html", autores = autorConsulta)

@app.route("/registrarAutor", methods=["POST"])
def registrarAutor():
    nombreA = request.form["nombreAutor"]
    fechaN = request.form["FeNac"]
    nac = request.form["nacionalidad"]
    autor = Autor(nombre_autor = nombreA, fecha_nac = fechaN, nacionalidad = nac )
    db.session.add(autor)
    db.session.commit()
    return "Autor registrado con éxito"

@app.route("/cargarDetalleAutor",methods=['POST'])
def cargarDetalleAutor():
    ID = request.form["idAutor"]
    autores = Autor.query.filter_by(id_autor = int(ID)).first()
    return render_template("autores/detalle_autor.html", autor = autores)

@app.route("/modificarAutor", methods=["POST"])
def modificarAutor():
    idAutor = request.form["idAutor"]
    nombreAutor = request.form["nombreAutor"]
    fechaNacimiento = request.form["fechaNacimiento"]
    nacionalidad = request.form["nacionalidad"]
    autor = Autor.query.filter_by(id_autor=int(idAutor)).first()
    #asignacion
    autor.nombre_autor = nombreAutor
    autor.fecha_nac = fechaNacimiento
    autor.nacionalidad = nacionalidad
    db.session.commit()
    return ("Autor modificado con éxito")

@app.route("/eliminarAutor", methods=["POST"])
def eliminarAutor():
    idAutor = request.form["idAutor"]
    autor = Autor.query.filter_by(id_autor=int(idAutor)).first()
    #asignacion
    db.session.delete(autor)
    db.session.commit()
    return ("Autor eliminado con éxito")
#terminan autores

#inicia genero
@app.route("/generos")
def generos():
    return render_template("generos/index.html")

@app.route("/cargarGeneros",methods=['POST'])
def cargarGeneros():
    generoConsulta = Genero.query.all()
    return render_template("generos/tabla_generos.html", generos = generoConsulta)

@app.route("/registrarGenero", methods=["POST"])
def registrargenero():
    nombreG = request.form["nombreGenero"]
    genero = Genero(nombre_genero = nombreG)
    db.session.add(genero)
    db.session.commit()
    return "Género registrado con éxito"

@app.route("/cargarDetalleGenero",methods=['POST'])
def cargarDetalleGenero():
    ID = request.form["idGenero"]
    generos = Genero.query.filter_by(id_genero = int(ID)).first()
    return render_template("generos/detalle_genero.html", genero = generos)

@app.route("/modificarGenero", methods=["POST"])
def modificarGenero():
    idGenero = request.form["idGenero"]
    nombreGenero = request.form["nombreGenero"]
    genero = Genero.query.filter_by(id_genero=int(idGenero)).first()
    #asignacion
    genero.nombre_genero = nombreGenero
    db.session.commit()
    return ("Género modificado con éxito")

@app.route("/eliminarGenero", methods=["POST"])
def eliminarGenero():
    idGenero = request.form["idGenero"]
    genero = Genero.query.filter_by(id_genero=int(idGenero)).first()
    #asignacion
    db.session.delete(genero)
    db.session.commit()
    return ("Género eliminado con éxito")
#termina genero

#inicia editorial
@app.route("/editoriales")
def editoriales():
    return render_template("editoriales/index.html")

@app.route("/cargarEditoriales",methods=['POST'])
def cargarEditoriales():
    editorialesConsulta = Editorial.query.all()
    return render_template("editoriales/tabla_editoriales.html", editoriales = editorialesConsulta)

@app.route("/registrarEditorial", methods=["POST"])
def registrarEditorial():
    nombreE = request.form["nombreEditorial"]
    editorial = Editorial(nombre_editorial= nombreE)
    db.session.add(editorial)
    db.session.commit()
    return "Editorial registrada"

@app.route("/cargarDetalleEditorial",methods=['POST'])
def cargarDetalleEditorial():
    ID = request.form["idEditorial"]
    editoriales = Editorial.query.filter_by(id_editorial = int(ID)).first()
    return render_template("editoriales/detalle_editorial.html", editorial = editoriales)

@app.route("/modificarEditorial", methods=["POST"])
def modificarEditorial():
    idEditorial = request.form["idEditorial"]
    nombreEditorial = request.form["nombreEditorial"]
    editorial = Editorial.query.filter_by(id_editorial=int(idEditorial)).first()
    #asignacion
    editorial.nombre_editorial = nombreEditorial
    db.session.commit()
    return ("Editorial modificada con éxito")

@app.route("/eliminarEditorial", methods=["POST"])
def eliminarEditorial():
    idEditorial = request.form["idEditorial"]
    editorial = Editorial.query.filter_by(id_editorial=int(idEditorial)).first()
    #asignacion
    db.session.delete(editorial)
    db.session.commit()
    return ("Editorial eliminado con éxito")
#termina editorial



#inicia registro usuarios
@app.route("/registrar")
def registrar():
    return render_template("registro.html");

@app.route("/registrarUsuario", methods=['POST'])
def registrarUsuario():
    email = request.form["email"]
    password = request.form["password"]
    password_cifrado = bcryp.generate_password_hash(password).decode('utf-8')
    usuario = Usuarios(email = email, password=password_cifrado)
    db.session.add(usuario)
    db.session.commit()
    return redirect("/")

#termina registro usuarios


if __name__ == '__main__':
    db.create_all()
    app.run();
