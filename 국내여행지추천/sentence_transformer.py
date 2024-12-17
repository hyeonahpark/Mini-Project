import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import gradio as gr
import numpy as np
import folium
import time
from summa import summarizer  # summarize 함수 사용
import re
import os  # 파일 존재 여부 확인
import torch

# GPU가 사용 가능한지 확인 후, GPU로 모델 로드
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 모델 로드
model = SentenceTransformer('jhgan/ko-sroberta-multitask', device=device)

path = 'C:/ai5/미니프로젝트/_data/TourAPI/'

# 축제 데이터 불러오기
festival_df = pd.read_csv(path + '축제.csv', on_bad_lines='skip').fillna("")
festival_df['광역시/도'] = festival_df['주소'].apply(lambda x: ' '.join(x.split()[:2]))

# 미리 계산된 임베딩 파일이 있는지 확인
embedding_file = path + "embedding.csv"

# 임베딩 파일이 있는 경우 로드
df = pd.read_csv(embedding_file)

# 임베딩 데이터를 배열로 변환
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))
df['embedding1'] = df['embedding1'].apply(lambda x: np.array(eval(x)))
df['embedding2'] = df['embedding2'].apply(lambda x: np.array(eval(x)))
df['embedding3'] = df['embedding3'].apply(lambda x: np.array(eval(x)))

df = df.sample(frac=1)

# HTML 태그 제거 함수
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# 가중치를 적용한 유사성 계산 함수
def chatbot(user):
    start_time = time.time()
    # 입력된 텍스트의 임베딩 (유저 입력에 대해서만 실시간으로 계산)
    embedding = model.encode(user)

    # 각 임베딩별 유사도 벡터화된 방식으로 계산
    df['similarity'] = cosine_similarity([embedding], np.vstack(df['embedding'].values)).squeeze()
    df['similarity_other_embedding_1'] = cosine_similarity([embedding], np.vstack(df['embedding1'].values)).squeeze()
    df['similarity_other_embedding_2'] = cosine_similarity([embedding], np.vstack(df['embedding2'].values)).squeeze()
    df['similarity_other_embedding_3'] = cosine_similarity([embedding], np.vstack(df['embedding3'].values)).squeeze()

    # 가중치를 설정
    weight1 = 0.05  # 대분류 가중치
    weight2 = 0.5   # 중분류 가중치
    weight3 = 0.2   # 광역시/도 가중치
    weight4 = 0.15  # 개요 가중치

    # 총합 유사도 계산
    df['total_similarity'] = (df['similarity'] * weight1 +
                              df['similarity_other_embedding_1'] * weight2 +
                              df['similarity_other_embedding_2'] * weight3 +
                              df['similarity_other_embedding_3'] * weight4)

    # 총합 유사도가 높은 상위 5개 관광지명 추출
    top_places = df.nlargest(5, 'total_similarity')[['명칭', '광역시/도', '개요']]

    # 요약된 설명 생성
    top_places['요약'] = top_places['개요'].apply(lambda x: remove_html_tags(summarizer.summarize(x, words=50)) if len(x.split()) > 50 else remove_html_tags(x))

    # 관광지명과 요약된 설명 리스트 생성
    recommended_info = []
    for idx, row in enumerate(top_places.itertuples(), start=1):
        recommended_info.append(f"{idx}. {row.명칭}\n{row.요약}")

    recommended_places_str = '\n\n'.join(recommended_info)

    # 상위 관광지 중 첫 번째 관광지의 광역시/도에서 열리는 축제 추천
    top_tourist_region = top_places.iloc[0]['광역시/도']
    related_festivals = festival_df[festival_df['광역시/도'] == top_tourist_region][:5]

    festivals_list = related_festivals['명칭'].tolist()
    festivals_str = ', '.join(festivals_list)

    ############################################### 지도 생성 #########################################################
    xy_coord = []
    for place in top_places['명칭']:
        place_data = df[df['명칭'] == place].iloc[0]
        latitude = place_data['위도']
        longitude = place_data['경도']
        xy_coord.append({'lon': longitude, 'lat': latitude, 'name': place})

    # 지도 객체 생성
    m = folium.Map(location=[xy_coord[0]['lat'], xy_coord[0]['lon']], zoom_start=10, tiles='OpenStreetMap')

    # 구글 맵 타일 추가
    folium.TileLayer(tiles='http://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                     attr='Google', name='Google Map', overlay=True, control=True).add_to(m)

    # 마커 추가
    for loc in xy_coord:
        folium.Marker([loc['lat'], loc['lon']], popup=loc['name']).add_to(m)

    # 지도 HTML 반환
    map_html = m._repr_html_()
    #######################################################################################################

    # 출력 형식 준비
    if festivals_list:
        result = f"{recommended_places_str}\n\n{top_tourist_region}에서 열리는 축제: {festivals_str}"
    else:
        result = recommended_places_str

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

    return result, map_html

# Gradio Blocks 사용하여 유저 입력창 밑에 지도 배치
with gr.Blocks() as demo:
    with gr.Column():
        user_input = gr.Textbox(label="질문을 입력하세요", placeholder="관광지 관련 질문을 입력해주세요")
        with gr.Row():
            text_output = gr.Textbox(label="추천 관광지")
            map_output = gr.HTML(label="지도")

        user_input.submit(chatbot, inputs=user_input, outputs=[text_output, map_output])

demo.launch(debug=False, share=True)
