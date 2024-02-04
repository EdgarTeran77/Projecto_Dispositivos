from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5433/dispositivos"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(20))

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String, index=True)
    apellido = db.Column(db.String)
    cedula = db.Column(db.String)
    correo = db.Column(db.String, unique=True, index=True)
    telefono = db.Column(db.String)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

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
    data = request.get_json()
    evento = Evento(**data)
    db.session.add(evento)
    db.session.commit()
    
    # Excluir el objeto no serializable al devolver la respuesta
    evento_dict = {
        "id": evento.id,
        "nombre": evento.nombre,
        "fecha": evento.fecha,
        "descripcion": evento.descripcion,
        "foto": evento.foto,
        "lugar": evento.lugar
        # Puedes agregar más campos según sea necesario
    }
    
    return jsonify(evento_dict)

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
    titulo = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False)

# Rutas para el CRUD de notificaciones

@app.route('/notificaciones', methods=['POST'])
def create_notificacion():
    data = request.get_json()
    notificacion = Notificacion(**data)
    db.session.add(notificacion)
    db.session.commit()
    return jsonify({"message": "Notificación creada exitosamente"}), 201

@app.route('/notificaciones', methods=['GET'])
def read_all_notificaciones():
    notificaciones = Notificacion.query.all()
    notificaciones_list = [{"id": notificacion.id, "titulo": notificacion.titulo, "contenido": notificacion.contenido, "fecha": notificacion.fecha} for notificacion in notificaciones]
    return jsonify(notificaciones_list)

@app.route('/notificaciones/<int:notificacion_id>', methods=['GET'])
def read_notificacion(notificacion_id):
    notificacion = Notificacion.query.get(notificacion_id)
    if notificacion:
        notificacion_dict = {"id": notificacion.id, "titulo": notificacion.titulo, "contenido": notificacion.contenido, "fecha": notificacion.fecha}
        return jsonify(notificacion_dict)
    return jsonify({"message": "Notificación no encontrada"}), 404

@app.route('/notificaciones/<int:notificacion_id>', methods=['PUT'])
def update_notificacion(notificacion_id):
    notificacion = Notificacion.query.get(notificacion_id)
    if notificacion:
        data = request.get_json()
        notificacion.titulo = data.get('titulo', notificacion.titulo)
        notificacion.contenido = data.get('contenido', notificacion.contenido)
        notificacion.fecha = data.get('fecha', notificacion.fecha)
        db.session.commit()
        return jsonify({"message": "Notificación actualizada exitosamente"}), 200
    return jsonify({"message": "Notificación no encontrada"}), 404

@app.route('/notificaciones/<int:notificacion_id>', methods=['DELETE'])
def delete_notificacion(notificacion_id):
    notificacion = Notificacion.query.get(notificacion_id)
    if notificacion:
        db.session.delete(notificacion)
        db.session.commit()
        return jsonify({"message": "Notificación eliminada exitosamente"}), 200
    return jsonify({"message": "Notificación no encontrada"}), 404


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



if __name__ == '__main__':
    app.run(debug=True)
