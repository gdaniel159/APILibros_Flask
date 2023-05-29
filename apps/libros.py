from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# Inicializamos la app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/libros?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creacion de la BD

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Creacion de la BD de Libros

class Libros(db.Model):

    id_libro = db.Column(db.Integer,primary_key=True)
    genero = db.Column(db.String(100),nullable=False)
    categoria = db.Column(db.String(100),nullable=False)
    titulo = db.Column(db.String(100),nullable=False)
    autor = db.Column(db.String(100),nullable=False)
    descripcion_autor = db.Column(db.String(255),nullable=False)
    sinopsis = db.Column(db.String(255),nullable=False)
    portada = db.Column(db.String(255),nullable=False)

    def __init__(self,id_libro,genero,categoria,titulo,autor,descripcion_autor,sinopsis,portada):

        self.id_libro = id_libro
        self.genero = genero
        self.categoria = categoria
        self.titulo = titulo
        self.autor = autor
        self.descripcion_autor = descripcion_autor
        self.sinopsis = sinopsis
        self.portada = portada  

with app.app_context():

    db.create_all()

# Aqui definiremos el esquema que seguira nuestra API para mostrarnos la informacion de la BD

class LibrosSchema(ma.Schema):

    class Meta:

        fields = ('id_libro','genero','categoria','titulo','autor','descripcion_autor','sinopsis','portada')

# Una sola respuesta

libro_schema = LibrosSchema()

# Cuando hayan muchas respuestas

libros_schema = LibrosSchema(many=True)

# ======= GET =======

@app.route('/libros',methods=['GET'])

def getLibros():

    # Traemos todos los datos usando una consulta select *

    all_libros = Libros.query.all()

    # Guardamos el resultado para luego convertirlo a un JSON

    result = libros_schema.dump(all_libros)

    response = jsonify(result)

    response.headers.add('Access-Control-Allow-Origin', '*')

    # Conversion a JSON

    return response

# ======= POST =======

# POST - Agregar un nuevo libro

@app.route('/libros', methods=['POST'])

def addLibro():

    # Obtener los datos del libro enviados en el cuerpo de la solicitud
    data = request.get_json()

    try:

        # Validar y deserializar los datos usando el esquema
        libro = libro_schema.load(data)
        # Crear una nueva instancia de Libros con los datos validados
        nuevo_libro = Libros(**libro)
        # Agregar el nuevo libro a la base de datos
        db.session.add(nuevo_libro)
        db.session.commit()
        # Retornar los datos del libro agregado en la respuesta
        return libro_schema.jsonify(nuevo_libro), 201
    
    except ma.ValidationError as err:

        # Si hay errores de validación, retornar los mensajes de error
        return jsonify(errors=err.messages), 400
    
# Ruta para actualizar un libro específico

@app.route('/libros/<int:id_libro>', methods=['PUT', 'PATCH'])

def updateLibro(id_libro):

    # Obtener los datos del libro enviado en el cuerpo de la solicitud
    data = request.get_json()

    try:

        # Obtener el libro existente de la base de datos

        libro = Libros.query.get(id_libro)

        if libro is None:

            return jsonify(message='Libro no encontrado'), 404
        

        # Actualizar los campos del libro con los nuevos valores

        if 'id_autor' in data:

            libro.id_autor = data['id_autor']

        if 'id_genero' in data:

            libro.id_genero = data['id_genero']

        if 'id_categoria' in data:

            libro.id_categoria = data['id_categoria']

        if 'titulo' in data:

            libro.titulo = data['titulo']

        if 'sinopsis' in data:

            libro.sinopsis = data['sinopsis']

        if 'portada' in data:

            libro.portada = data['portada']

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Retornar los datos del libro actualizado en la respuesta
        return libro_schema.jsonify(libro), 200
    
    except ma.ValidationError as err:
        
        # Si hay errores de validación, retornar los mensajes de error
        return jsonify(errors=err.messages), 400

# Mensaje de Bienvenida

if __name__ == '__main__':

    app.run(debug=True)