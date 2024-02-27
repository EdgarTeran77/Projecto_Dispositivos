from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt , decode_token
from werkzeug.security import generate_password_hash, check_password_hash  # Importar check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os, io, base64, uuid
from PIL import Image
from dotenv import load_dotenv
from modelo import  EventRecommender
from datetime import datetime,timezone



app = Flask(__name__)
CORS(app)

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Ahora puedes acceder a las variables de entorno como si fueran variables regulares de Python
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = os.getenv("DB_PORT")

app.config['SECRET_KEY'] = 'dispositivos1225555..+'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + ':' + DB_PORT + '/' + DB_DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'gffdgrebgbynngnn,,,yhdf'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=200)
db = SQLAlchemy(app)
jwt = JWTManager(app)

UPLOAD_FOLDER = 'C:\\Users\\edgar\\OneDrive\\Documentos\\GitHub\\Projecto_Dispositivos\\images\\perfil'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, index=True)
    apellido = db.Column(db.String)
    cedula = db.Column(db.String)
    correo = db.Column(db.String, unique=True, index=True)
    telefono = db.Column(db.String)
    contraseña = db.Column(db.String)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    imagen = db.Column(db.String)

class UsuarioGusto(db.Model):
    __tablename__ = 'usuario_gusto'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    gusto_id = db.Column(db.Integer, db.ForeignKey('gustos.id'))

    def __init__(self, usuario_id, gusto_id):
        self.usuario_id = usuario_id
        self.gusto_id = gusto_id

def get_unique_filename(filename):
    # Generar un UUID único
    unique_identifier = str(uuid.uuid4())
    # Obtener la extensión del archivo
    extension = os.path.splitext(filename)[1]
    # Concatenar el UUID y la extensión para crear un nombre de archivo único
    unique_filename = unique_identifier + extension
    return unique_filename


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo_usuario = data.get('correo')
    contraseña = data.get('contraseña')

    # Validar si los datos de inicio de sesión están presentes
    if not correo_usuario or not contraseña:
        return jsonify({"message": "Correo o contraseña faltantes"}), 400

    # Verificar si el correo electrónico es válido
    if not correo_usuario:
        return jsonify({"message": "Correo electrónico inválido"}), 400

    # Verificar si la contraseña es válida
    if not contraseña:
        return jsonify({"message": "Contraseña inválida"}), 400

    # Intentar encontrar al usuario en la base de datos
    usuario = Usuario.query.filter_by(correo=correo_usuario).first()  

    # Validar si se encontró al usuario
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Validar si la contraseña ingresada coincide con la contraseña almacenada (hash)
    if not check_password_hash(usuario.contraseña, contraseña):
        return jsonify({"message": "Contraseña incorrecta"}), 401

    # Generar el token de acceso
    access_token = create_access_token(identity=usuario.id)

    # Obtener el ID del usuario
    usuario_id = usuario.id

    # Verificar si el usuario tiene gustos completados
    gustos_completados = UsuarioGusto.query.filter_by(usuario_id=usuario.id).count() > 0
    print (access_token)
    # Devolver la respuesta con el valor de gustos_completados y el ID del usuario
    return jsonify({
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "user_id": usuario_id,
        "gustos_completados": gustos_completados
    }), 200

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        telefono = data.get('telefono')
        password = data.get('password') 
        cedula = data.get('cedula')

        print('Datos del formulario:')
        print('Nombre:', nombre)
        print('Apellido:', apellido)
        print('Correo:', correo)
        print('Teléfono:', telefono)
        print('Contraseña:', password)
        print('Cedula:', cedula)

        if 'imagen' not in request.files:
            return jsonify({"message": "No se proporcionó una imagen"}), 400

        imagen = request.files['imagen']
        print(imagen)
        # Verificar si se proporcionó un archivo
        if imagen.filename == '':
            return jsonify({"message": "No se seleccionó ningún archivo"}), 400

        # Imprimir el nombre del archivo de la imagen
        print('Nombre del archivo de la imagen:', imagen.filename)

        # Verificar si el archivo es una imagen permitida
        if not allowed_file(imagen.filename):
            return jsonify({"message": "Tipo de archivo no permitido"}), 400

        # Generar un nombre de archivo único
        unique_filename = get_unique_filename(imagen.filename)

        # Guardar la imagen en el sistema de archivos con el nombre único
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        imagen.save(filepath)

        print('Filepath:', filepath)  # Agrega este mensaje para verificar el filepath
        print('llego hasta aqui')
        
        hashed_password = generate_password_hash(password)  # Cambiado de 'contraseña' a 'password'
        print(hashed_password)
        print('Intentando guardar en la base de datos...')  # Agrega este mensaje para verificar el proceso de guardado

        # Guardar la ruta de la imagen en la base de datos
        nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo,
                        telefono=telefono, contraseña=hashed_password, imagen=filepath)
        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            print('Usuario guardado exitosamente en la base de datos.')
        except Exception as e:
            db.session.rollback()
            print('Error al guardar en la base de datos:', str(e))
            return jsonify({"message": "Error al crear el usuario", "error": str(e)}), 500

        return jsonify({"message": "Usuario creado exitosamente"}), 201
    except Exception as e:
        # En caso de error, deshacer la transacción y devolver un mensaje de error
        db.session.rollback()
        return jsonify({"message": "Error al crear el usuario", "error": str(e)}), 500



@app.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    print(request.files)
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontró la imagen en la solicitud'}), 400

    imagen_file = request.files['imagen']
    print(imagen_file)
    if isinstance(imagen_file, FileStorage):
        imagen_bytes = imagen_file.read()
        try:
        # Intenta abrir los datos de la imagen con PIL
            imagen = Image.open(io.BytesIO(imagen_bytes))
            imagen.show()
        except Exception as e:
            print(f"Error al abrir los datos de la imagen: {e}")

        try:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt'), 'w') as f:
                f.write('test')
            print('El directorio es accesible')
        except Exception as e:
            print(f'Error al acceder al directorio: {e}')


        try:
            # Guardar la imagen en el servidor
            nombre_archivo = 'perfil_usuario.jpg'  # Nombre de archivo predefinido o genera un nombre único
            with open(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo), 'wb') as f:
                f.write(imagen_bytes)

            return jsonify({'mensaje': 'Imagen recibida correctamente'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'La imagen recibida no es válida'}), 400


@app.route('/check-email', methods=['POST'])
def check_email_availability():
    data = request.get_json()
    correo = data.get('correo')

    # Verificar si el correo electrónico ya está en uso en la base de datos
    usuario_existente = Usuario.query.filter_by(correo=correo).first()

    if usuario_existente:
        return jsonify({'message': 'El correo electrónico ya está en uso'}), 200

    return jsonify({'message': 'El correo electrónico está disponible'}), 200

@app.route('/user_id')
@jwt_required()
def get_user_id():
    # Obtener el ID del usuario desde el token JWT
    user_id = get_jwt_identity()
    
    # Devolver el ID del usuario en formato JSON
    return jsonify({"id": user_id}), 200

@app.route('/profile')
@jwt_required()
def profile():
    # Obtener el ID del usuario desde el token JWT
    user_id = get_jwt_identity()
    
    # Consultar la información del usuario utilizando su ID
    usuario = Usuario.query.get(user_id)
    
    if usuario:
        # Construir la ruta completa de la imagen de perfil
        imagen_path = usuario.imagen if usuario.imagen else None
        
        # Si hay una imagen, leerla como datos binarios y convertirla a base64
        imagen_base64 = None
        if imagen_path:
            with open(imagen_path, 'rb') as file:
                imagen_data = file.read()
                imagen_base64 = base64.b64encode(imagen_data).decode('utf-8')
        
        # Devolver los datos del usuario y la imagen en formato JSON
        data = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "cedula": usuario.cedula,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "imagen_base64": imagen_base64
        }
        
        return jsonify(data), 200
    else:
        return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/guardar-gustos', methods=['POST'])
def guardar_gustos():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        gustos_seleccionados = data.get('gustos')

        # Verificar si se proporcionó el ID del usuario
        if not usuario_id:
            return jsonify({"message": "No se proporcionó el ID de usuario"}), 400

        # Verificar si se proporcionaron gustos
        if not gustos_seleccionados:
            return jsonify({"message": "No se proporcionaron gustos"}), 400

        # Iterar sobre los gustos seleccionados y guardar la relación en la tabla UsuarioGusto
        for gusto_id in gustos_seleccionados:
            # Crear una instancia de UsuarioGusto con el usuario_id y el gusto_id
            nueva_relacion = UsuarioGusto(usuario_id=usuario_id, gusto_id=gusto_id)
            db.session.add(nueva_relacion)

        # Confirmar la transacción
        db.session.commit()

        return jsonify({"message": "Gustos guardados exitosamente"}), 200
    except Exception as e:
        # En caso de error, deshacer la transacción y devolver un mensaje de error
        db.session.rollback()
        return jsonify({"message": "Error al guardar los gustos", "error": str(e)}), 500


# Ruta para cerrar sesión y revocar el token JWT
@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    # Obtener el token JWT
    jwt_token = get_jwt()  # Cambiado aquí

    # Agregar el token a la lista de tokens revocados
    # De esta manera, el token ya no será válido para futuras solicitudes
    jwt.revoked_token_store.add(jwt_token['jti'])
    
    return jsonify({"message": "Sesión cerrada exitosamente"}), 200

    
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(20))


class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String, index=True)
    fecha = db.Column(db.String)
    descripcion = db.Column(db.String)
    foto = db.Column(db.String)
    lugar = db.Column(db.String)

@app.route('/usuarios', methods=['POST'])
def create_user():
    data = request.get_json()
    user = Usuario(**data)
    db.session.add(user)
    db.session.commit()
    
    # Excluir el objeto no serializable al devolver la respuesta
    user_dict = {
        "id": user.id,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "cedula": user.cedula,
        "correo": user.correo,
        "telefono": user.telefono,
        "rol_id": user.rol_id
        # Puedes agregar más campos según sea necesario
    }
    
    return jsonify(user_dict)

@app.route('/usuarios', methods=['GET'])
def read_all_users():
    users = Usuario.query.all()
    users_list = [{"id": user.id, "nombre": user.nombre, "apellido": user.apellido, "cedula": user.cedula,
                   "correo": user.correo, "telefono": user.telefono, "rol_id": user.rol_id} for user in users]
    return jsonify(users_list)

@app.route('/usuarios/<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = Usuario.query.get(user_id)
    if user:
        user_dict = {
            "id": user.id,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "cedula": user.cedula,
            "correo": user.correo,
            "telefono": user.telefono,
            "rol_id": user.rol_id
        }
        return jsonify(user_dict)
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/usuarios/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Usuario.query.get(user_id)
    if user:
        data = request.get_json()
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        user_dict = {
            "id": user.id,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "cedula": user.cedula,
            "correo": user.correo,
            "telefono": user.telefono,
            "rol_id": user.rol_id
        }
        return jsonify(user_dict)
    return jsonify({"message": "Usuario no encontrado"}), 404

@app.route('/usuarios/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Usuario.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado"})
    return jsonify({"message": "Usuario no encontrado"}), 404


@app.route('/eventos', methods=['POST'])
def create_evento():
    try:
        data = request.form
        print("Datos recibidos del frontend:", data)
        evento = Evento(
            nombre=data.get('nombre'),
            fecha=data.get('fecha'),
            descripcion=data.get('descripcion'),
            lugar=data.get('lugar')
        )
        db.session.add(evento)
        db.session.commit()

        # Guardar la ruta de la imagen si se proporciona
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '':
                # Generar un nombre de archivo único
                unique_filename = get_unique_filename(imagen.filename)
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                # Guardar la imagen en la carpeta especificada
                imagen.save(filepath)
                # Actualizar el campo de foto en el evento con la ruta de la imagen
                evento.foto = filepath
                db.session.commit()

        evento_dict = {
            "id": evento.id,
            "nombre": evento.nombre,
            "fecha": evento.fecha,
            "descripcion": evento.descripcion,
            "foto": evento.foto,  # Devolver la ruta de la imagen en la respuesta JSON
            "lugar": evento.lugar
        }

        return jsonify(evento_dict), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el evento", "error": str(e)}), 500
    

@app.route('/eventos', methods=['GET'])
def read_all_eventos():
    eventos = Evento.query.all()
    eventos_list = [{"id": evento.id, "nombre": evento.nombre, "fecha": evento.fecha,
                     "descripcion": evento.descripcion, "foto": evento.foto, "lugar": evento.lugar} for evento in eventos]
    return jsonify(eventos_list)

@app.route('/eventos/<int:evento_id>', methods=['GET'])
def read_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if evento:
        evento_dict = {
            "id": evento.id,
            "nombre": evento.nombre,
            "fecha": evento.fecha,
            "descripcion": evento.descripcion,
            "foto": evento.foto,
            "lugar": evento.lugar
        }
        return jsonify(evento_dict)
    return jsonify({"message": "Evento no encontrado"}), 404

@app.route('/eventos/futuros', methods=['GET'])
def read_all_eventos_futuros():
    try:
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        print("Fecha actual:", fecha_actual)  # Imprimir la fecha actual
        
        # Filtrar los eventos futuros
        eventos_futuros = Evento.query.filter(Evento.fecha >= fecha_actual).all()
        
        eventos_list = []
        for evento in eventos_futuros:
            # Verificar si el evento tiene la columna 'foto'
            if hasattr(evento, 'foto'):
                # Obtener la ruta de la imagen del evento
                imagen_path = evento.foto if evento.foto else None
                print("Ruta de la imagen:", imagen_path)  # Imprimir la ruta de la imagen
                
                # Verificar si la ruta de la imagen existe
                if imagen_path and os.path.exists(imagen_path):
                    # Si hay una imagen y la ruta existe, leerla como datos binarios y convertirla a base64
                    with open(imagen_path, 'rb') as file:
                        imagen_data = file.read()
                        imagen_base64 = base64.b64encode(imagen_data).decode('utf-8')
                else:
                    # Si la ruta de la imagen no existe, asignar None a imagen_base64
                    imagen_base64 = None
            else:
                # Si el evento no tiene la columna 'foto', asignar None a imagen_base64
                imagen_base64 = None
            
            # Crear un diccionario con los datos del evento, incluida la imagen en base64
            evento_data = {
                "id": evento.id,
                "nombre": evento.nombre,
                "fecha": evento.fecha,
                "descripcion": evento.descripcion,
                "foto_base64": imagen_base64,  # Agregar la imagen en base64
                "lugar": evento.lugar
            }
            eventos_list.append(evento_data)
        
        print("Eventos obtenidos:", eventos_list)  # Imprimir los eventos obtenidos
        return jsonify(eventos_list), 200
    
    except Exception as e:
        print("Error al obtener eventos futuros:", str(e))  # Imprimir el error en caso de excepción
        return jsonify({"message": "Error al obtener eventos futuros", "error": str(e)}), 500

@app.route('/eventos/<int:evento_id>', methods=['PUT'])
def update_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if evento:
        data = request.get_json()
        for key, value in data.items():
            setattr(evento, key, value)
        db.session.commit()
        evento_dict = {
            "id": evento.id,
            "nombre": evento.nombre,
            "fecha": evento.fecha,
            "descripcion": evento.descripcion,
            "foto": evento.foto,
            "lugar": evento.lugar
        }
        return jsonify(evento_dict)
    return jsonify({"message": "Evento no encontrado"}), 404

@app.route('/eventos/<int:evento_id>', methods=['DELETE'])
def delete_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if evento:
        db.session.delete(evento)
        db.session.commit()
        return jsonify({"message": "Evento eliminado"})
    return jsonify({"message": "Evento no encontrado"}), 404

with app.app_context():
    db.create_all()

class Gusto(db.Model):
    __tablename__ = 'gustos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

@app.route('/gustos', methods=['POST'])
def create_gusto():
    data = request.get_json()
    gusto = Gusto(**data)
    db.session.add(gusto)
    db.session.commit()
    return jsonify({"message": "Gusto creado exitosamente"}), 201

@app.route('/gustos', methods=['GET'])
def read_all_gustos():
    gustos = Gusto.query.all()
    gustos_list = [{"id": gusto.id, "nombre": gusto.nombre, "descripcion": gusto.descripcion} for gusto in gustos]
    return jsonify(gustos_list)

@app.route('/gustos/<int:gusto_id>', methods=['GET'])
def read_gusto(gusto_id):
    gusto = Gusto.query.get(gusto_id)
    if gusto:
        gusto_dict = {"id": gusto.id, "nombre": gusto.nombre, "descripcion": gusto.descripcion}
        return jsonify(gusto_dict)
    return jsonify({"message": "Gusto no encontrado"}), 404

@app.route('/gustos/<int:gusto_id>', methods=['PUT'])
def update_gusto(gusto_id):
    gusto = Gusto.query.get(gusto_id)
    if gusto:
        data = request.get_json()
        gusto.nombre = data.get('nombre', gusto.nombre)
        gusto.descripcion = data.get('descripcion', gusto.descripcion)
        db.session.commit()
        return jsonify({"message": "Gusto actualizado exitosamente"}), 200
    return jsonify({"message": "Gusto no encontrado"}), 404

@app.route('/gustos/<int:gusto_id>', methods=['DELETE'])
def delete_gusto(gusto_id):
    gusto = Gusto.query.get(gusto_id)
    if gusto:
        db.session.delete(gusto)
        db.session.commit()
        return jsonify({"message": "Gusto eliminado exitosamente"}), 200
    return jsonify({"message": "Gusto no encontrado"}), 404


class Facultad(db.Model):
    __tablename__ = 'facultades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

# Rutas para el CRUD de facultades

@app.route('/facultades', methods=['POST'])
def create_facultad():
    data = request.get_json()
    facultad = Facultad(**data)
    db.session.add(facultad)
    db.session.commit()
    return jsonify({"message": "Facultad creada exitosamente"}), 201

@app.route('/facultades', methods=['GET'])
def read_all_facultades():
    facultades = Facultad.query.all()
    facultades_list = [{"id": facultad.id, "nombre": facultad.nombre, "descripcion": facultad.descripcion} for facultad in facultades]
    return jsonify(facultades_list)

@app.route('/facultades/<int:facultad_id>', methods=['GET'])
def read_facultad(facultad_id):
    facultad = Facultad.query.get(facultad_id)
    if facultad:
        facultad_dict = {"id": facultad.id, "nombre": facultad.nombre, "descripcion": facultad.descripcion}
        return jsonify(facultad_dict)
    return jsonify({"message": "Facultad no encontrada"}), 404

@app.route('/facultades/<int:facultad_id>', methods=['PUT'])
def update_facultad(facultad_id):
    facultad = Facultad.query.get(facultad_id)
    if facultad:
        data = request.get_json()
        facultad.nombre = data.get('nombre', facultad.nombre)
        facultad.descripcion = data.get('descripcion', facultad.descripcion)
        db.session.commit()
        return jsonify({"message": "Facultad actualizada exitosamente"}), 200
    return jsonify({"message": "Facultad no encontrada"}), 404

@app.route('/facultades/<int:facultad_id>', methods=['DELETE'])
def delete_facultad(facultad_id):
    facultad = Facultad.query.get(facultad_id)
    if facultad:
        db.session.delete(facultad)
        db.session.commit()
        return jsonify({"message": "Facultad eliminada exitosamente"}), 200
    return jsonify({"message": "Facultad no encontrada"}), 404


class Lugar(db.Model):
    __tablename__ = 'lugares'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    descripcion = db.Column(db.Text)

# Rutas para el CRUD de lugares

@app.route('/lugares', methods=['POST'])
def create_lugar():
    data = request.get_json()
    lugar = Lugar(**data)
    db.session.add(lugar)
    db.session.commit()
    return jsonify({"message": "Lugar creado exitosamente"}), 201

@app.route('/lugares', methods=['GET'])
def read_all_lugares():
    lugares = Lugar.query.all()
    lugares_list = [{"id": lugar.id, "nombre": lugar.nombre, "direccion": lugar.direccion, "descripcion": lugar.descripcion} for lugar in lugares]
    return jsonify(lugares_list)

@app.route('/lugares/<int:lugar_id>', methods=['GET'])
def read_lugar(lugar_id):
    lugar = Lugar.query.get(lugar_id)
    if lugar:
        lugar_dict = {"id": lugar.id, "nombre": lugar.nombre, "direccion": lugar.direccion, "descripcion": lugar.descripcion}
        return jsonify(lugar_dict)
    return jsonify({"message": "Lugar no encontrado"}), 404

@app.route('/lugares/<int:lugar_id>', methods=['PUT'])
def update_lugar(lugar_id):
    lugar = Lugar.query.get(lugar_id)
    if lugar:
        data = request.get_json()
        lugar.nombre = data.get('nombre', lugar.nombre)
        lugar.direccion = data.get('direccion', lugar.direccion)
        lugar.descripcion = data.get('descripcion', lugar.descripcion)
        db.session.commit()
        return jsonify({"message": "Lugar actualizado exitosamente"}), 200
    return jsonify({"message": "Lugar no encontrado"}), 404

@app.route('/lugares/<int:lugar_id>', methods=['DELETE'])
def delete_lugar(lugar_id):
    lugar = Lugar.query.get(lugar_id)
    if lugar:
        db.session.delete(lugar)
        db.session.commit()
        return jsonify({"message": "Lugar eliminado exitosamente"}), 200
    return jsonify({"message": "Lugar no encontrado"}), 404


class Negocio(db.Model):
    __tablename__ = 'negocios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    descripcion = db.Column(db.Text)

# Rutas para el CRUD de negocios

@app.route('/negocios', methods=['POST'])
def create_negocio():
    data = request.get_json()
    negocio = Negocio(**data)
    db.session.add(negocio)
    db.session.commit()
    return jsonify({"message": "Negocio creado exitosamente"}), 201

@app.route('/negocios', methods=['GET'])
def read_all_negocios():
    negocios = Negocio.query.all()
    negocios_list = [{"id": negocio.id, "nombre": negocio.nombre, "direccion": negocio.direccion, "descripcion": negocio.descripcion} for negocio in negocios]
    return jsonify(negocios_list)

@app.route('/negocios/<int:negocio_id>', methods=['GET'])
def read_negocio(negocio_id):
    negocio = Negocio.query.get(negocio_id)
    if negocio:
        negocio_dict = {"id": negocio.id, "nombre": negocio.nombre, "direccion": negocio.direccion, "descripcion": negocio.descripcion}
        return jsonify(negocio_dict)
    return jsonify({"message": "Negocio no encontrado"}), 404

@app.route('/negocios/<int:negocio_id>', methods=['PUT'])
def update_negocio(negocio_id):
    negocio = Negocio.query.get(negocio_id)
    if negocio:
        data = request.get_json()
        negocio.nombre = data.get('nombre', negocio.nombre)
        negocio.direccion = data.get('direccion', negocio.direccion)
        negocio.descripcion = data.get('descripcion', negocio.descripcion)
        db.session.commit()
        return jsonify({"message": "Negocio actualizado exitosamente"}), 200
    return jsonify({"message": "Negocio no encontrado"}), 404

@app.route('/negocios/<int:negocio_id>', methods=['DELETE'])
def delete_negocio(negocio_id):
    negocio = Negocio.query.get(negocio_id)
    if negocio:
        db.session.delete(negocio)
        db.session.commit()
        return jsonify({"message": "Negocio eliminado exitosamente"}), 200
    return jsonify({"message": "Negocio no encontrado"}), 404


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensaje = db.Column(db.Text)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación con la tabla de usuarios
    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True))

    def __repr__(self):
        return f"<Notificacion {self.id}>"

# Rutas CRUD para Notificacion
@app.route('/notificaciones', methods=['GET'])
@jwt_required()
def get_notificaciones():
    current_user_id = get_jwt_identity()
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user_id).all()
    output = []
    for notificacion in notificaciones:
        output.append({
            'id': notificacion.id,
            'usuario_id': notificacion.usuario_id,
            'mensaje': notificacion.mensaje,
            'leida': notificacion.leida,
            'fecha': notificacion.fecha,
        })
    return jsonify({'notificaciones': output})

@app.route('/notificaciones/<id>', methods=['GET'])
def get_notificacion(id):
    notificacion = Notificacion.query.get_or_404(id)
    return jsonify({
        'id': notificacion.id,
        'usuario_id': notificacion.usuario_id,
        'mensaje': notificacion.mensaje,
        'leida': notificacion.leida,
        'fecha': notificacion.fecha,
    })

@app.route('/notificaciones', methods=['POST'])
@jwt_required()  # Requiere que el usuario esté autenticado con un token JWT válido
def create_notificacion():
    try:
        # Obtiene el ID de usuario del token JWT
        current_user_id = get_jwt_identity()

        # Obtiene los datos de la solicitud
        data = request.get_json()

        app.logger.debug("Datos recibidos para la notificación: %s", data)  # Agregar print para depuración

        # Verificar si los datos recibidos contienen todos los campos necesarios
        if 'mensaje' not in data:
            raise ValueError("El campo 'mensaje' es requerido")

        # Crear una nueva notificación asociada al usuario actual
        nueva_notificacion = Notificacion(
            usuario_id=current_user_id,
            mensaje=data.get('mensaje'),
            leida=data.get('leida', False),
            fecha = datetime.now(timezone.utc)
        )

        app.logger.debug("Notificación creada: %s", nueva_notificacion.__dict__)  # Agregar print para depuración

        # Guardar la nueva notificación en la base de datos
        db.session.add(nueva_notificacion)
        db.session.commit()

        return jsonify({'message': 'Notificación creada exitosamente'}), 201
    except Exception as e:
        app.logger.error("Error al crear la notificación: %s", str(e))  # Agregar print para depuración
        return jsonify({'error': str(e)}), 500


@app.route('/notificaciones/<id>', methods=['PUT'])
def update_notificacion(id):
    notificacion = Notificacion.query.get_or_404(id)
    data = request.get_json()
    notificacion.usuario_id = data['usuario_id']
    notificacion.mensaje = data['mensaje']
    notificacion.leida = data.get('leida', notificacion.leida)
    notificacion.otro_atributo = data.get('otro_atributo', notificacion.otro_atributo)
    db.session.commit()
    return jsonify({'message': 'Notificacion actualizada exitosamente'})

@app.route('/notificaciones/<id>', methods=['DELETE'])
def delete_notificacion(id):
    notificacion = Notificacion.query.get_or_404(id)
    db.session.delete(notificacion)
    db.session.commit()
    return jsonify({'message': 'Notificacion eliminada exitosamente'})

class Servicio(db.Model):
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    costo = db.Column(db.Float, nullable=False)

# Rutas para el CRUD de servicios

@app.route('/servicios', methods=['POST'])
def create_servicio():
    data = request.get_json()
    servicio = Servicio(**data)
    db.session.add(servicio)
    db.session.commit()
    return jsonify({"message": "Servicio creado exitosamente"}), 201

@app.route('/servicios', methods=['GET'])
def read_all_servicios():
    servicios = Servicio.query.all()
    servicios_list = [{"id": servicio.id, "nombre": servicio.nombre, "descripcion": servicio.descripcion, "costo": servicio.costo} for servicio in servicios]
    return jsonify(servicios_list)

@app.route('/servicios/<int:servicio_id>', methods=['GET'])
def read_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)
    if servicio:
        servicio_dict = {"id": servicio.id, "nombre": servicio.nombre, "descripcion": servicio.descripcion, "costo": servicio.costo}
        return jsonify(servicio_dict)
    return jsonify({"message": "Servicio no encontrado"}), 404

@app.route('/servicios/<int:servicio_id>', methods=['PUT'])
def update_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)
    if servicio:
        data = request.get_json()
        servicio.nombre = data.get('nombre', servicio.nombre)
        servicio.descripcion = data.get('descripcion', servicio.descripcion)
        servicio.costo = data.get('costo', servicio.costo)
        db.session.commit()
        return jsonify({"message": "Servicio actualizado exitosamente"}), 200
    return jsonify({"message": "Servicio no encontrado"}), 404

@app.route('/servicios/<int:servicio_id>', methods=['DELETE'])
def delete_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)
    if servicio:
        db.session.delete(servicio)
        db.session.commit()
        return jsonify({"message": "Servicio eliminado exitosamente"}), 200
    return jsonify({"message": "Servicio no encontrado"}), 404


@app.route('/recommend-events/')
@jwt_required()
def recommend_events():
    try:
        user_id = get_jwt_identity()
        print(user_id)
        db_params = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + ':' + DB_PORT + '/' + DB_DATABASE
        event_recommender = EventRecommender(db_params)
        event_recommender.connect_to_database()
        recommended_events_ids = event_recommender.recommend_events_for_user(user_id)
        # Dentro de tu método donde quieres filtrar los eventos futuros por los IDs recomendados
        eventos_recomendados = Evento.query.filter(Evento.id.in_(recommended_events_ids)).all()
        eventos_list = [{"id": evento.id, "nombre": evento.nombre, "fecha": evento.fecha,
                 "descripcion": evento.descripcion, "foto": evento.foto, "lugar": evento.lugar} for evento in eventos_recomendados]
        
        # Devolver los eventos recomendados en formato JSON
        return jsonify({"recommended_events": eventos_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5001")
    app.run(debug=True)
