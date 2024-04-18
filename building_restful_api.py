from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from typing import List
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:itsyapassword69@localhost/restful_api"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

class Members(Base):
    __tablename__ = "Members"
    member_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(320))
    phone: Mapped[str] = mapped_column(db.String(15))

class WorkoutSessions(Base):
    __tablename__ = "WorkoutSessions"
    session_id: Mapped[int] = mapped_column(primary_key=True)
    focus: Mapped[str] = mapped_column(db.String(255))
    date: Mapped[datetime.date] = mapped_column(db.Date, nullable=False)

with app.app_context():
    db.create_all()


class MembersSchema(ma.Schema):
    member_id = fields.Integer(required=False)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("member_id", "name", "email", "phone")

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)

class SessionsSchema(ma.Schema):
    session_id = fields.Integer(required=False)
    focus = fields.String(required=True)
    date = fields.String(required=True)

sessions_schema = SessionsSchema(many=True)
session_schema = SessionsSchema()


@app.route("/")
def home():
    return "Welcome to Fitness Center!"

# ============================================== GET ========================================

@app.route("/members", methods = ["GET"])
def get_members():
    query = select(Members)
    result = db.session.execute(query).scalars()
    members = result.all()

    return members_schema.jsonify(members)


@app.route("/sessions", methods = ["GET"])
def get_sessions():
    query = select(WorkoutSessions)
    result = db.session.execute(query).scalars()
    sessions = result.all()

    return sessions_schema.jsonify(sessions)

# ============================================== ADD ========================================

@app.route("/members", methods = ["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session:
        new_member = Members(name = member_data['name'], email = member_data['email'], phone = member_data["phone"])
        session.add(new_member)
        session.commit()
    
    return jsonify({"message": "New member successfully added"}), 201

@app.route("/sessions", methods = ["POST"])
def add_session():
    try:
        session_data = sessions_schema.load(request.json)
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session:
        new_session = WorkoutSessions(focus = session_data['focus'], date = session_data["date"])
        session.add(new_session)
        session.commit()
    
    return jsonify({"message": "New session successfully added"}), 201

# ======================================== PUT ==========================================

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(Members).filter(Members.member_id==id)
            result = session.execute(query).scalars().first()
            if result is None:
                return jsonify({"error": "Member Not Found"}), 404
            member = result

            try:
                member_data = member_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in member_data.items():
                setattr(member, field, value)

            session.commit()
    return jsonify({"message": "Member details updated succesfully"}), 200

@app.route("/sessions/<int:id>", methods=["PUT"])
def update_session(id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(Session).filter(WorkoutSessions.session_id==id)
            result = session.execute(query).scalars().first()
            if result is None:
                return jsonify({"error": "Member Not Found"}), 404
            member = result

            try:
                member_data = member_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in member_data.items():
                setattr(member, field, value)

            session.commit()
    return jsonify({"message": "Session details updated succesfully"}), 200




# ======================================= DELETE ========================================

@app.route("/members/<int:id>", methods = ["DELETE"])
def delete_member(id):
    delete_statement = delete(Members).where(Members.member_id==id)

    with db.session.begin():
        result = db.session.execute(delete_statement)

        if result.rowcount == 0:
            return jsonify({"error": "Member not found"}), 404
        
        return jsonify({"message": "Member removed successfully"}), 200

@app.route("/sessions/<int:id>", methods = ["DELETE"])
def delete_session(id):
    delete_statement = delete(Session).where(WorkoutSessions.session_id==id)

    with db.session.begin():
        result = db.session.execute(delete_statement)

        if result.rowcount == 0:
            return jsonify({"error": "Session not found"}), 404
        
        return jsonify({"message": "Session removed successfully"}), 200



if __name__ == "__main__":
    app.run(debug=True)

#  run as python file

