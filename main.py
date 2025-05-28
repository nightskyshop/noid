from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import PhotoSession
import qrcode, io, base64, os, uuid, image
from PIL import Image
from io import BytesIO

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

    photoSession = db_session.query(PhotoSession).filter(PhotoSession.id == session).first()

    if not photoSession:
        return jsonify({'result': False, 'message': '존재하지 않거나 마감된 세션입니다.'}), 400
    
    

    try:
        first = request.files['first']
        second = request.files['second']
        third = request.files['third']
        fourth = request.files['fourth']
    except Exception as e:
        return jsonify({'result': False, 'message': '필요한 파라미터를 모두 입력해주세요.'}), 400

    files = [first, second, third, fourth]
    data = []

    for i in range(len(files)):
        file = files[i]
        try:
            file_bytes = file.read()
            file.seek(0)
            
            try:
                Image.open(BytesIO(file_bytes))
            except Exception as e:
                return jsonify({'result': False, 'message': f'유효하지 않은 이미지 파일입니다: {file.filename}'}), 400
            
            data.append(base64.b64encode(file_bytes).decode("utf-8"))
        except Exception as e:
            return jsonify({'result': False, 'message': f'파일 처리 중 오류가 발생했습니다: {str(e)}'}), 400

    try:
        photo = image.create(data, photoSession.frame, session)
    except Exception as e:
        return jsonify({'result': False, 'message': f'이미지 처리 중 오류가 발생했습니다: {str(e)}'}), 400

    qr = qrcode.make(f"https://localhost:3000/download?session={session}", border=4, box_size=20)
    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    if photoSession:
        photoSession.qrfile = img_base64
        photoSession.photofile = photo

    db_session.commit()

    return jsonify({'result': True, 'message': '성공적으로 이미지를 업로드하였습니다.', 'qrcode': img_base64, 'photo': photo}), 200

@app.route("/download", methods=["GET"])
def download():
    session = request.args.get('session') # http://#DOMAIN/download?session={uuid}
    if not session:
        return render_template('forbidden.html')
    
    photoSession = db_session.query(PhotoSession).filter(PhotoSession.id == session).first()

    if not photoSession:
        return render_template('forbidden.html')
    
    return render_template('download.html', session=session, image_path=f'./download_image?session={session}')

    
@app.route('/download_image', methods=["GET"])
def download_image():
    session = request.args.get('session')
    if not session:
        return render_template('forbidden.html')
    
    photoSession = db_session.query(PhotoSession).filter(PhotoSession.id == session).first()

    if not photoSession:
        return render_template('forbidden.html')
    
    return send_file(f'./images/{session}.png', as_attachment=True)

if __name__== "__main__":
	app.debug = True
	app.run(host="0.0.0.0", port=8000)