from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kdramas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class KDrama(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

kdrama_parser = reqparse.RequestParser()
kdrama_parser.add_argument('title', type=str, required=True, help="Title cannot be blank!")
kdrama_parser.add_argument('director', type=str, required=True, help="Director cannot be blank!")
kdrama_parser.add_argument('genre', type=str, required=True, help="Genre cannot be blank!")
kdrama_parser.add_argument('year', type=int, required=True, help="Year cannot be blank!")

class KDramaListResource(Resource):
    def get(self):
        genre = request.args.get('genre')
        if genre:
            kdramas = KDrama.query.filter(func.lower(KDrama.genre) == genre.lower()).all()
        else:
            kdramas = KDrama.query.all()
        return [{'id': k.id, 'title': k.title, 'director': k.director, 'genre': k.genre, 'year': k.year} for k in kdramas]

    def post(self):
        args = kdrama_parser.parse_args()
        new_kdrama = KDrama(title=args['title'], director=args['director'], genre=args['genre'], year=args['year'])
        db.session.add(new_kdrama)
        db.session.commit()
        return {'message': 'K-Drama added successfully!', 'kdrama': {'id': new_kdrama.id}}, 201

class KDramaResource(Resource):
    def patch(self, kdrama_id):
        kdrama = KDrama.query.get(kdrama_id)
        if not kdrama:
            return {'message': 'K-Drama not found'}, 404
        args = kdrama_parser.parse_args()
        kdrama.title = args['title']
        kdrama.director = args['director']
        kdrama.genre = args['genre']
        kdrama.year = args['year']
        db.session.commit()
        return {'message': 'K-Drama updated successfully!'}

    def delete(self, kdrama_id):
        kdrama = KDrama.query.get(kdrama_id)
        if not kdrama:
            return {'message': 'K-Drama not found'}, 404
        db.session.delete(kdrama)
        db.session.commit()
        return {'message': 'K-Drama deleted successfully!'}

api.add_resource(KDramaListResource, '/kdramas')
api.add_resource(KDramaResource, '/kdramas/<int:kdrama_id>')

if __name__ == '__main__':
    app.run(debug=True)
