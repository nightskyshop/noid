from flask import Flask, jsonify, request, render_template, send_file, make_response
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import PhotoSession, Base #Base 추가함.
import qrcode, io, base64, os, uuid, image
from PIL import Image
from io import BytesIO


app = Flask(__name__)
CORS(app) # Cross Origin 정책 설정

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/frame", methods=['GET'])
def frame():
    return render_template('frame.html')

@app.route("/noid_select", methods=['GET'])
def noid_select():
    return render_template('noid_select.html')

@app.route("/noid_dankook_b", methods=['GET'])
def noid_dankook_b():
    return render_template('/noid_dankook_b.html')

@app.route("/noid_dankook_n", methods=['GET'])
def noid_dankook_w():
    return render_template('/noid_dankook_n.html')

@app.route("/ddp_select", methods=['GET'])
def ddp_select():
    return render_template('/ddp_select.html')

@app.route("/ddp_dwyl", methods=['GET'])
def ddp_dwyl():
    return render_template('/ddp_dwyl.html')

@app.route("/ddp_seoul", methods=['GET'])
def ddp_seoul():
    return render_template('/ddp_seoul.html')

@app.route("/n_select", methods=['GET'])
def n_select():
    return render_template('/n_select.html')

@app.route("/n_green", methods=['GET'])
def n_green():
    return render_template('/n_green.html')

@app.route("/n_blue", methods=['GET'])
def n_blue():
    return render_template('/n_blue.html')

@app.route("/take_photo-1", methods=['GET'])
def take_photo_1():
    return render_template('/take_photo-1.html')

@app.route("/take_photo-2", methods=['GET'])
def take_photo_2():
    return render_template('/take_photo-2.html')

@app.route("/take_select_photo", methods=['GET'])
def take_select_photo():
    return render_template('/take_select_photo.html')

@app.route("/forbidden", methods=['GET'])
def forbidden():
    return render_template('/forbidden.html')

engine = create_engine('sqlite:///db.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

@app.route("/api/session", methods=['POST'])
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
            print("createSession error : ", e)
            return jsonify({"message": "error", "error": str(e)}), 500
        finally:
            db_session.close()
    except Exception as e:
        return jsonify({'result': False, 'message': '필수 파라미터가 누락되었습니다.'}), 400

@app.route("/api/upload", methods=['POST'])
def upload():
    try:
        session = request.form['session']
    except Exception as e:

        return jsonify({'result': False, 'message': '필수 파라미터 session이 누락되었습니다.'}), 400

    photoSession = db_session.query(PhotoSession).filter(PhotoSession.id == session).first()

    if not photoSession:
        return jsonify({'result': False, 'message': '존재하지 않거나 마감된 세션입니다.'}), 400

    try:
        first = request.files['photo1']
        second = request.files['photo2']
        third = request.files['photo3']
        fourth = request.files['photo4']
    except Exception as e:
        print(e)
        return jsonify({'result': False, 'message': '필요한 파라미터 photo가 누락되었습니다.'}), 400

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
        print(e)
        return jsonify({'result': False, 'message': f'이미지 처리 중 오류가 발생했습니다: {str(e)}'}), 400

    qr = qrcode.make(f"http://download.noid.my/download?session={session}", border=4, box_size=20)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    if photoSession:
        photoSession.qrfile = img_base64
        photoSession.photofile = photo

    db_session.commit()

    photo_bytes = base64.b64decode(photo)
    files = {
        'file': (f'{session}.png', BytesIO(photo_bytes), 'image/png')
    }

    try:
        response = requests.post(
            "http://download.noid.my/upload?password=8krybwTfjJEIFq8J50CfEJlyFMlxYNl04pZDcgXKPz8pY3E362",
            files=files,
            #verify=False  # HTTPS가 self-signed인 경우
        )
        print("업로드 서버 응답:", response.status_code, response.text)
    except Exception as e:
        print("업로드 서버 전송 오류:", str(e))

    return jsonify({'result': True, 'message': '성공적으로 이미지를 업로드하였습니다.', 'qrcode': img_base64, 'photo': photo}), 200

@app.route("/download", methods=["GET"])
def downloadQR():
    session = request.args.get('session')
    if not session:
        return render_template("forbidden.html")
    
    photoSession = db_session.query(PhotoSession).filter(PhotoSession.id == session).first()

    if not photoSession:
        return render_template("forbidden.html")
    
    return render_template("download_qrcode.html", selected_photo=photoSession.photofile, qr_code=photoSession.qrfile)

app.run(port=3000, debug=True)