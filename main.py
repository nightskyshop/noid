from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import PhotoSession
import qrcode, io, base64, os, uuid

app = Flask(__name__)
CORS(app)

engine = create_engine('sqlite:///db.db')
Session = sessionmaker(bind=engine)
db_session = Session()

@app.route('/session', methods=['POST'])
def createSession():
    try:
        frame = request.form['frame']

        try:
            id = str(uuid.uuid4())

            photo_session = PhotoSession(id=id, frame=frame)
            db_session.add(photo_session)
            db_session.commit()

            return jsonify({"sessionID": id})
        except Exception as e:
            db_session.rollback()
            return jsonify({"message": "error", "error": str(e)}), 500
        finally:
            db_session.close()
    except Exception as e:
        return jsonify({'result': False, 'message': '필수 파라미터가 누락되었습니다.'}), 400
    
    

@app.route('/upload', methods=['POST'])
def upload():

    try:
        session = request.form['session']
    except Exception as e:
        return jsonify({'result': False, 'message': '필수 파라미터가 누락되었습니다.'}), 400


    if db_session.query(db_session.query.filter(PhotoSession.id == session).exists()).scalar():
        return jsonify({'result': False, 'message': '존재하지 않거나 마감된 세션입니다.'}), 400

    first = request.files['first']
    second = request.files['second']
    third = request.files['third']
    fourth = request.files['fourth']

    files = [first, second, third, fourth]

    for i in range(len(files)):
        file = files[i]
        filename = secure_filename(file.filename)
        print(f"filename: {filename}")
        os.makedirs("images", exist_ok=True)
        file.save(os.path.join("./images", filename))
    
    return jsonify({"message": "success" })
    
    

if __name__== "__main__":
	app.debug = True
	app.run(host="0.0.0.0", port=8000)