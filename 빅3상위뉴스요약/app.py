from flask import Flask, render_template
from news import news
import datetime

app = Flask(__name__)

@app.route('/')         # 애플리케이션의 기본 URL(http://localhost:5000/)에 대한 요청이 들어오면 index 함수를 실행
def index():
    result = news()     # news 함수가 호출되어 뉴스 데이터를 가져옴
    data = datetime.date.today()    # 현재 날짜를 가져옴
    result = [result, data]
    return render_template('index.html', result=result)   # templates라는 이름의 폴더를 기본 경로로 설정, templates 폴더 속 index.html 파일에 작성된 html 내용을 출력해서 보여줌  

if __name__ == '__main__':  # 해당 스크립트가 직접 실행될 때만 조건문 안의 코드를 실행, 파일이 직접 실행될 때는 Flask 서버가 실행되지만, 다른 파일에서 모듈로 임포트될 때는 서버가 실행되지 않음
    app.run(debug=True)     # 디버그 모드로 Flask 서버를 실행, 코드를 수정하면 서버를 자동으로 재시작하고, 에러 발생 시 디버그 정보를 제공



