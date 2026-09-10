import streamlit as st
import pandas as pd

st.set_page_config(page_title="WMS 倉庫管理システム", layout="wide")

st.title("📦 クラウド型 WMS（倉庫管理システム）")
st.caption("拠点: DPL草加 (GMTradings)")

# パスワード認証機能
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.subheader("🔒 ログイン")
        password = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if password == "1234":  # ←初期パスワード（変更可能）
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが違います")
        return False
    return True

if check_password():
    # データベースの初期設定
    if "inventory_db" not in st.session_state:
        st.session_state["inventory_db"] = pd.DataFrame([
            {"ロケ名": "3C-1-4-4", "商品コード": "755851", "商品名1": "コーナン インナークッション", "引当済数": 0, "未引当数": 1, "在庫日": "2026/06/05", "品質区分名": "良品"},
            {"ロケ名": "3B-T4-2-4", "商品コード": "273386", "商品名1": "レンジマグカップ ブラウン", "引当済数": 0, "未引当数": 163, "在庫日": "2026/06/16", "品質区分名": "良品"},
            {"ロケ名": "3B-T5-2-4", "商品コード": "121186", "商品名1": "モデルナ IHウォックパン 20cm", "引当済数": 2, "未引当数": 69, "在庫日": "2026/06/08", "品質区分名": "良品"}
        ])

    tab_search, tab_move, tab_import = st.tabs(["🔍 在庫検索・一覧 (PC用)", "🚚 ロケーション移動 (スマホ用)", "📥 CSVデータ一括取り込み"])

    # 1. 在庫検索
    with tab_search:
        st.subheader("在庫検索・フィルター")
        df = st.session_state["inventory_db"]
        col1, col2 = st.columns(2)
        with col1:
            keyword = st.text_input("🔍 商品コード・商品名で検索", "")
        with col2:
            locations = ["すべて"] + sorted(list(df["ロケ名"].astype(str).unique()))
            selected_loc = st.selectbox("📍 ロケーションで絞り込み", locations)
            
        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[filtered_df["商品コード"].astype(str).str.contains(keyword, case=False) | filtered_df["商品名1"].astype(str).str.contains(keyword, case=False)]
        if selected_loc != "すべて":
            filtered_df = filtered_df[filtered_df["ロケ名"] == selected_loc]

        st.dataframe(filtered_df, use_container_width=True)

    # 2. ロケーション移動
    with tab_move:
        st.subheader("📱 現場ロケーション移動処理")
        df = st.session_state["inventory_db"]
        code_input = st.text_input("1. 商品コードを入力", "")
        if code_input:
            target_items = df[df["商品コード"].astype(str) == code_input]
            if not target_items.empty:
                st.success(f"該当商品: {target_items.iloc[0]['商品名1']}")
                current_loc = st.selectbox("2. 移動元ロケーションを選択", target_items["ロケ名"].tolist())
                current_row = target_items[target_items["ロケ名"] == current_loc].iloc[0]
                new_loc = st.text_input("3. 移動先ロケーションを入力", "")
                move_qty = st.number_input("4. 移動数量", min_value=1, max_value=int(current_row['未引当数']), value=1)
                
                if st.button("🚚 移動を確定"):
                    idx = df[(df["商品コード"].astype(str) == code_input) & (df["ロケ名"] == current_loc)].index[0]
                    st.session_state["inventory_db"].at[idx, "未引当数"] -= move_qty
                    
                    new_idx = df[(df["商品コード"].astype(str) == code_input) & (df["ロケ名"] == new_loc)].index
                    if not new_idx.empty:
                        st.session_state["inventory_db"].at[new_idx[0], "未引当数"] += move_qty
                    else:
                        new_row = current_row.copy()
                        new_row["ロケ名"] = new_loc
                        new_row["未引当数"] = move_qty
                        st.session_state["inventory_db"] = pd.concat([st.session_state["inventory_db"], pd.DataFrame([new_row])], ignore_index=True)
                    st.success("移動が完了しました！")
            else:
                st.error("商品が見つかりません")

    # 3. CSV取り込み
    with tab_import:
        st.subheader("📥 既存在庫CSVデータの取り込み")
        uploaded_file = st.file_uploader("在庫_明細.csvを選択してください", type=["csv"])
        if uploaded_file is not None:
            new_df = pd.read_csv(uploaded_file)
            st.dataframe(new_df.head(), use_container_width=True)
            if st.button("データベースに適用（上書き）"):
                st.session_state["inventory_db"] = new_df
                st.success("取り込みが完了しました！")
