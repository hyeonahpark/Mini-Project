import requests
from bs4 import BeautifulSoup
from newspaper import Article
from summa.summarizer import summarize
from newspaper import Config
import requests

def news():
    # 언론사별 네이버 뉴스 검색 결과 페이지 URL (해당 언론사의 뉴스만 필터링한 결과 페이지)
    new_url_list = ['https://search.naver.com/search.naver?where=news&query=%EB%89%B4%EC%8A%A4&sm=tab_opt&sort=0&photo=3&field=0&pd=0&ds=&de=&docid=&related=0&mynews=1&office_type=1&office_section_code=1&news_office_checked=1020&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0',
                    'https://search.naver.com/search.naver?where=news&query=%EB%89%B4%EC%8A%A4&sm=tab_opt&sort=0&photo=3&field=0&pd=0&ds=&de=&docid=&related=0&mynews=1&office_type=1&office_section_code=1&news_office_checked=1025&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0',
                    'https://search.naver.com/search.naver?where=news&query=%EB%89%B4%EC%8A%A4&sm=tab_opt&sort=0&photo=3&field=0&pd=0&ds=&de=&docid=&related=0&mynews=1&office_type=1&office_section_code=1&news_office_checked=1028&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0'
                ]

    # 언론사별 뉴스 상세 페이지의 URL 패턴 (기사 본문 URL을 필터링하기 위해 사용)
    new_name_url_list = ['https://www.donga.com/news/',  # 동아일보 기사 URL 패턴
                        'https://www.joongang.co.kr/article/',  # 중앙일보 기사 URL 패턴
                        'https://www.hani.co.kr/arti/'  # 한겨례 기사 URL 패턴
                        ]
    news_summaries = []
    # 각 언론사별로 반복문을 통해 주요 뉴스를 크롤링
    for index, sec_url in enumerate(new_url_list):
        ## BeautifulSoup 객체 생성
        # 주어진 URL로부터 HTML 데이터를 가져와 파싱하는 함수
        def get_soup_obj(url):
            # User-Agent는 브라우저에서 보내는 요청처럼 보이게 하기 위한 헤더 정보
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}     
            res = requests.get(url, headers=headers)  # 주어진 URL에 HTTP GET 요청을 보냄
            # print(res.text) # URL에서 가져온 HTML 데이터를 출력 (디버깅 용도)
            
            # HTML 데이터를 lxml 파서를 사용해 BeautifulSoup 객체로 변환
            soup = BeautifulSoup(res.text, 'lxml')  
            return soup 

        # 해당 언론사 페이지의 상위 뉴스 HTML을 가져옴
        soup = get_soup_obj(sec_url)

        # 네이버 뉴스 검색 결과에서 뉴스 링크를 모두 추출 (div 태그의 class가 "group_news"인 곳에서 찾음)
        url_list = soup.find('div', class_="group_news").find_all("a")
        # HTML 구조상 div 태그 안에서 a 태그(링크)를 모두 가져옴
        
        news_url_list = ['']  # 뉴스 URL을 저장할 리스트 (처음에 빈 문자열로 초기화)

        ## 중복되는 링크 및 '#' 같은 불필요한 링크를 제외하고 원하는 뉴스 링크만 필터링
        for url in url_list:
            # 링크가 특정 언론사(news_name_url_list[index])의 URL 패턴과 일치하는지 확인
            if url['href'][:len(new_name_url_list[index])] == new_name_url_list[index]:
                # 이전 링크와 중복되는 경우를 제외
                if (news_url_list[-1] == url['href']):
                    continue
                else:
                    news_url_list.append(url['href'])  # 새로운 링크는 리스트에 추가
            else:
                continue

        news_url_list.remove('')  # 초기화했던 빈 문자열을 삭제

        # 내용 요약 함수 (기사 본문을 요약)
        def summarize_content(content):
            try:
                # 본문 길이가 300자 이상일 때만 요약 (짧은 본문은 요약하지 않음)
                if len(content) > 300:
                    summary = summarize(content, ratio=0.3)  # summa 라이브러리를 사용하여 요약 (비율: 30%)
                    summary = summary.replace('광고', '')       # 광고 단어 제거
                else:
                    summary = content  # 본문이 짧을 경우 원문 그대로 반환
            except ValueError:
                summary = '원문 없음'  # 요약이 불가능한 경우의 예외 처리
            return summary

        # 크롤링한 뉴스 URL들에 대해 기사 내용을 가져오고 요약
        for url in news_url_list[:3]:
            # newspaper 모듈을 사용할 때 타임아웃 오류 방지를 위한 설정
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
            config = Config()  # newspaper3k 모듈의 Config 객체 생성
            config.browser_user_agent = user_agent  # 브라우저의 User-Agent 설정
            config.request_timeout = 20  # 요청 타임아웃 설정
            
            # newspaper 모듈을 사용하여 기사 다운로드 및 파싱
            article = Article(url, language='ko', config=config)  # 한국어 설정
            article.download()  # URL에서 기사를 다운로드
            article.parse()  # 기사 내용을 파싱하여 title과 text 속성을 채움
            title = article.title  # 기사 제목
            contents = article.text  # 기사 본문 내용
            summary = summarize_content(contents)  # 본문을 요약
            news_summaries.append({
                'title': title,  # 기사 제목 저장
                'summary': summary  # 요약된 기사 내용 저장
            })
    return news_summaries
