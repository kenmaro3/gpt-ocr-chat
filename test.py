import streamlit as st
import os
import pandas as pd
from sqlalchemy import create_engine
import json
from ocr import process_pdf
import openai
from chat import build_chat, build_chat

openai_key = ""
openai.api_key = openai_key

MODEL_NAME = "gpt-3.5-turbo-16k-0613"
MODEL_TEMPERATURE = 0.9

# 環境変数に設定
os.environ['OPENAI_API_KEY'] = openai_key


# データベース接続のためのエンジンを作成
db_engine = create_engine('sqlite:///app_database.db')

# Streamlitアプリケーションのタイトルと説明を設定
st.title("人事チャットアプリ")
st.write("PDFファイルをアップロードし、関数を呼び出して結果を表示し、データベースに保存します。")

# ファイルのアップロードを受け付けるコンポーネントを作成
uploaded_file = st.file_uploader("履歴書ファイルをアップロードしてください", type=["pdf"])

# アップロードされたファイルのパスを表示
if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write("アップロードされたファイルの詳細:", file_details)

    # アップロードされたPDFファイルを一時的なディレクトリに保存
    with st.spinner("ファイルを保存しています..."):
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
    st.success("ファイルが正常に保存されました。")

    # 関数を呼び出してPDFを処理し、結果を取得
    # ここではダミーの関数を示します。実際の関数に置き換えてください。
    # def process_pdf(file_path):
    #     # ここにPDF処理の実際のコードを書く
    #     result = {"message": "PDF処理が完了しました。", "data": {"sample_data": 42}}
    #     return result
    with st.spinner("OCR及び構造化を処理しています..."):
        result = process_pdf(file_path)

    # 結果をJSON形式で表示
    st.write("PDF処理結果:")
    st.json(result)

    # 結果をデータベースに保存
    with db_engine.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pdf_results (id INTEGER PRIMARY KEY AUTOINCREMENT, result_json TEXT)"
        )
        conn.execute(
            "INSERT INTO pdf_results (result_json) VALUES (?)", (json.dumps(result),)
        )

    # 次のページに遷移
    st.write("\n\n")
    st.title("AIチャットページ")  # "遷移ページ" と表示
    st.write("AI人事にn候補者について質問できます。")

# データベースから結果を読み込む
with db_engine.connect() as conn:
    results = conn.execute("SELECT * FROM pdf_results")
    results_df = pd.read_sql("SELECT * FROM pdf_results", conn)

# 結果を表示
if not results_df.empty:
    st.write("データベースに保存された結果:")
    for index, row in results_df.iterrows():
        if st.button(f"クリックして結果を表示 (ID: {row['id']})"):
            st.json(json.loads(row['result_json']))
else:
    st.write("データベースにはまだ結果が保存されていません。")


# ファイルのアップロードを受け付けるコンポーネントを作成
uploaded_file = st.file_uploader("職務経歴書をアップロードしてください", type=["pdf"])

# アップロードされたファイルのパスを表示
if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write("アップロードされたファイルの詳細:", file_details)

    # アップロードされたPDFファイルを一時的なディレクトリに保存
    with st.spinner("ファイルを保存しています..."):
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
    st.success("ファイルが正常に保存されました。")

    # 関数を呼び出してPDFを処理し、結果を取得
    # ここではダミーの関数を示します。実際の関数に置き換えてください。
    # def process_pdf(file_path):
    #     # ここにPDF処理の実際のコードを書く
    #     result = {"message": "PDF処理が完了しました。", "data": {"sample_data": 42}}
    #     return result
    with st.spinner("AI人事を準備しています..."):
        qa = build_chat(file_path)

    # メッセージ履歴を保持するリストの定義
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # メッセージ履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:= st.chat_input("候補者について知りたいことはありますか？"):

            # ユーザーによる質問の保存・表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        query = f"あなたは人事として候補者についての質問に答えるChatBotです。次の質問に答えてください。:{prompt}"
        res = qa.run(query)

        # LLMによる回答の表示
        with st.chat_message("assistant"):
            st.markdown(res)

        # LLMによる回答の保存
        st.session_state.messages.append({"role": "assistant", "content": res})

    # # 結果をJSON形式で表示
    # st.write("PDF処理結果:")
    # st.json(result)

    # # をデータベースに保存
    # with db_engine.connect() as conn:
    #     conn.execute(
    #         "CREATE TABLE IF NOT EXISTS pdf_results (id INTEGER PRIMARY KEY AUTOINCREMENT, result_json TEXT)"
    #     )
    #     conn.execute(
    #       "INSERT INTO pdf_results (result_json) VALUES (?)", (json.dumps(result),)
    #   )
